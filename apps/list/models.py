# Django imports
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.core.validators import MaxLengthValidator
from django.core.files.uploadedfile import InMemoryUploadedFile
# Python imports
import os
from io import BytesIO
import sys
from PIL import Image
# Local imports
from apps.logic.services import main_website_source_set
from apps.list.managers import ListManager, ListRatingManager
from apps.source.models import Source
from apps.article.models import Article
# New Imports

User = get_user_model()


def create_list_pic_name(self, filename):
    path = "list_pic/"
    format = f"{self.creator.username} - {filename}"
    return os.path.join(path, format)

class List(models.Model):
    list_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, validators=[MaxLengthValidator(30)])
    slug = models.SlugField()
    creator = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    subscribers = models.ManyToManyField(User, related_name='subscriber_list', blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    list_pic = models.ImageField(null=True, blank=True, upload_to=create_list_pic_name)
    is_public = models.BooleanField(default=False)
    sources = models.ManyToManyField(Source, related_name='lists', blank=True)
    articles = models.ManyToManyField(Article, related_name='articles_list', blank=True)
    main_website_source = models.CharField(max_length=100, blank=True)
    average_rating = models.FloatField(blank=True, null=True)
    ammount_of_ratings = models.IntegerField(default=0, null=True)

    class Meta:
        ordering = ('name', )

    objects = ListManager()

    @property
    def get_average_rating(self):
        return ListRating.objects.get_average_rating(self.list_id)

    @property
    def get_ammount_of_ratings(self):
        return ListRating.objects.get_ammount_of_ratings(self.list_id)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_list_pic = self.list_pic

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if self.__original_list_pic != self.list_pic:
            im = Image.open(self.list_pic)
            output = BytesIO()
            im = im.resize((175, 175))
            im.save(output, format='WEBP', quality=99)
            output.seek(0)
            self.list_pic = InMemoryUploadedFile(output, 'ImageField', "%s.webp" % self.list_pic.name.split('.')[0], 'image/webp', sys.getsizeof(output), None)
        elif self._state.adding is False:
            instance = main_website_source_set(self)
            super(List, instance).save(*args, **kwargs)
        super(List, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('list:list-details', kwargs={'profile_slug': self.creator.profile.slug ,'list_slug': self.slug})

    def __str__(self):
        return self.name


@receiver(m2m_changed, sender=List.sources.through)
def list_main_website_source_calculate(sender, instance, action, *args,
                                       **kwargs):
    if action == "post_add" or action == "post_remove":
        instance = main_website_source_set(instance)
        instance.save()

class ListRating(models.Model):
    list_rating_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, validators=[MaxValueValidator(5), MinValueValidator(0),])

    objects = ListRatingManager()

    def save(self, *args, **kwargs):
        super(ListRating, self).save(*args, **kwargs)
        rated_list = get_object_or_404(List, list_id=self.list.list_id)
        rated_list.average_rating = ListRating.objects.get_average_rating(self.list.list_id)
        rated_list.ammount_of_ratings = ListRating.objects.get_ammount_of_ratings(self.list.list_id)
        rated_list.save()

    def __str__(self):
        return f'{self.user} - {self.list} - {self.rating}'