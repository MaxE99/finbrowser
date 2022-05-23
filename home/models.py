# Django imports
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.template.defaultfilters import slugify
from django.urls import reverse
from accounts.models import Website
# Local imports
from home.logic.services import main_website_source_set
from home.managers import (ListManager, SourceManager, ArticleManager,
                           HighlightedArticlesManager, ListRatingManager,
                           SourceRatingManager)

User = get_user_model()


class Sector(models.Model):
    sector_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Sector, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('home:sector-details', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name


class Source(models.Model):
    PAYWALL_CHOICES = [('Yes', 'Yes'), ('Semi', 'Semi'), ('No', 'No')]
    WEBSITE_CHOICES = [('Medium', 'Medium'), ('Other', 'Other'),
                       ('SeekingAlpha', 'SeekingAlpha'),
                       ('Substack', 'Substack'), ('Twitter', 'Twitter'),
                       ('YouTube', 'YouTube')]
    source_id = models.AutoField(primary_key=True)
    url = models.URLField(unique=True)
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100, blank=True, unique=True)
    subscribers = models.ManyToManyField(User,
                                         related_name='subscriber_source',
                                         blank=True)
    favicon_path = models.CharField(max_length=500, blank=True)
    paywall = models.CharField(max_length=10,
                               choices=PAYWALL_CHOICES,
                               default='None')
    website = models.ForeignKey(Website, blank=True, null=True, on_delete=models.SET_NULL)
    top_source = models.BooleanField(default=False)
    about_text = models.TextField(blank=True)
    sector = models.ManyToManyField(Sector, related_name='sectors', blank=True)
    external_id = models.CharField(unique=True, null=True, blank=True, max_length=100)
    last_article_title = models.CharField(max_length=500, null=True, blank=True)

    objects = SourceManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        # if not self.name:
        #     self.name = self.domain.capitalize()
        # elif 'seekingalpha.com' not in self.url and 'twitter.com' not in self.url:
        #     self.domain = self.url.replace("https://",
        #                                    "").replace("www.",
        #                                                "").split('.')[0]
        #     self.favicon_path = f'home/favicons/{self.domain}.png'
        # Aufpassen SeekingAlpha nicht zu scrappen, bevor ich noch gebannt werde
        # website_scrapping_initiate(self.url, self.domain)
        super(Source, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('source:profile', kwargs={'slug': self.slug})

    def __str__(self):
        return self.slug


class ExternalSource(models.Model):
    external_source_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    website_name = models.CharField(max_length=100, blank=True)
    sector = models.ManyToManyField(Sector,
                                    related_name='external_sectors',
                                    blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.website_name}'


class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=500)
    link = models.URLField()
    pub_date = models.DateTimeField()
    source = models.ForeignKey(Source, blank=True, null=True, on_delete=models.SET_NULL)
    external_source = models.ForeignKey(ExternalSource, blank=True,
                                        null=True,
                                        on_delete=models.SET_NULL)
    external_id = models.CharField(unique=True, null=True, blank=True, max_length=100)

    objects = ArticleManager()

    def __str__(self):
        return self.title


class List(models.Model):
    list_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    creator = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    subscribers = models.ManyToManyField(User,
                                         related_name='subscriber_list',
                                         blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    list_pic = models.ImageField(null=True, blank=True, upload_to="list_pic")
    is_public = models.BooleanField(default=False)
    sources = models.ManyToManyField(Source, related_name='lists', blank=True)
    articles = models.ManyToManyField(Article,
                                      related_name='articles_list',
                                      blank=True)
    main_website_source = models.CharField(max_length=100, blank=True)

    objects = ListManager()

    @property
    def get_average_rating(self):
        return ListRating.objects.get_average_rating(self.list_id)

    @property
    def get_ammount_of_ratings(self):
        return ListRating.objects.get_ammount_of_ratings(self.list_id)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if self._state.adding is False:
            instance = main_website_source_set(self)
            super(List, instance).save(*args, **kwargs)
        else:
            super(List, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('home:list-details', kwargs={'profile_slug': self.creator.profile.slug ,'list_slug': self.slug})

    def __str__(self):
        return self.name


@receiver(m2m_changed, sender=List.sources.through)
def list_main_website_source_calculate(sender, instance, action, *args,
                                       **kwargs):
    if action == "post_add" or action == "post_remove":
        instance = main_website_source_set(instance)
        instance.save()


class SourceRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0,
                                 validators=[
                                     MaxValueValidator(5),
                                     MinValueValidator(0),
                                 ])

    objects = SourceRatingManager()

    def __str__(self):
        return f'{self.user} - {self.source} - {self.rating}'


class ListRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0,
                                 validators=[
                                     MaxValueValidator(5),
                                     MinValueValidator(0),
                                 ])

    objects = ListRatingManager()

    def __str__(self):
        return f'{self.user} - {self.list} - {self.rating}'


class HighlightedArticle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)

    objects = HighlightedArticlesManager()

    def __str__(self):
        return f'{self.user} - {self.article}'


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list = models.ForeignKey(List, on_delete=models.CASCADE, null=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, null=True)

    def __str__(self):
        if self.list:
            return f'{self.user} - {self.list}'
        else:
            return f'{self.user} - {self.source}'


class NotificationMessage(models.Model):
    notification_message_id = models.AutoField(primary_key=True)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    date = models.DateTimeField()
    user_has_seen = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.notification} - {self.article}'