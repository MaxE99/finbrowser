# Django imports
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from django.contrib.auth import get_user_model
# Local imports
from home.logic.scrapper import website_scrapping_initiate
from home.logic.services import main_website_source_set

User = get_user_model()


class Source(models.Model):
    PAYWALL_CHOICES = [('Yes', 'Yes'), ('Semi', 'Semi'), ('No', 'No')]
    WEBSITE_CHOICES = [('Medium', 'Medium'), ('Other', 'Other'),
                       ('SeekingAlpha', 'SeekingAlpha'),
                       ('Substack', 'Substack'), ('Twitter', 'Twitter'),
                       ('YouTube', 'YouTube')]
    source_id = models.AutoField(primary_key=True)
    url = models.URLField(unique=True)
    domain = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100, blank=True)
    subscribers = models.ManyToManyField(User,
                                         related_name='subscriber_source',
                                         blank=True)
    favicon_path = models.CharField(max_length=500, blank=True)
    paywall = models.CharField(max_length=10,
                               choices=PAYWALL_CHOICES,
                               default='None')
    website = models.CharField(max_length=100,
                               choices=WEBSITE_CHOICES,
                               default='None')
    about_text = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.domain.capitalize()
        elif 'seekingalpha.com' not in self.url and 'twitter.com' not in self.url:
            self.domain = self.url.replace("https://",
                                           "").replace("www.",
                                                       "").split('.')[0]
            self.favicon_path = f'home/favicons/{self.domain}.png'
        # Aufpassen SeekingAlpha nicht zu scrappen, bevor ich noch gebannt werde
        # website_scrapping_initiate(self.url, self.domain)
        super(Source, self).save(*args, **kwargs)

    def __str__(self):
        return self.domain


class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=500)
    link = models.URLField(unique=True)
    pub_date = models.DateField()
    source = models.ForeignKey(Source, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title


class List(models.Model):
    CONTENT_CHOICES = [('Articles', 'Articles'), ('Sources', 'Sources')]
    list_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    subscribers = models.ManyToManyField(User,
                                         related_name='subscriber_list',
                                         blank=True)
    content_type = models.CharField(max_length=10,
                                    choices=CONTENT_CHOICES,
                                    default='None')
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=False)
    sources = models.ManyToManyField(Source, related_name='lists', blank=True)
    main_website_source = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding is False:
            instance = main_website_source_set(self)
            super(List, instance).save(*args, **kwargs)
        else:
            super(List, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


@receiver(m2m_changed, sender=List.sources.through)
def list_main_website_source_calculate(sender, instance, action, *args,
                                       **kwargs):
    if action == "post_add" or action == "post_remove":
        instance = main_website_source_set(instance)
        instance.save()


class Sector(models.Model):
    list_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    sources = models.ManyToManyField(Source,
                                     related_name='sectors',
                                     blank=True)

    def __str__(self):
        return self.name


class BrowserCategory(models.Model):
    # user = UserModel
    browser_category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class BrowserSource(models.Model):
    # user = UserModel
    browser_source_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(BrowserCategory,
                                 null=True,
                                 on_delete=models.SET_NULL)
    source = models.ForeignKey(Source, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.source} - {self.category}'
