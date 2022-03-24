# Django imports
from django.db import models


class Source(models.Model):
    PAYWALL_CHOICES = [('Yes', 'Yes'), ('Semi', 'Semi'), ('No', 'No')]
    source_id = models.AutoField(primary_key=True)
    url = models.URLField(unique=True)
    domain = models.CharField(max_length=100, blank=True)
    favicon_path = models.CharField(max_length=500, blank=True)
    paywall = models.CharField(max_length=10,
                               choices=PAYWALL_CHOICES,
                               default='None')

    def save(self, *args, **kwargs):
        self.domain = self.url.replace("https://",
                                       "").replace("www.", "").split('.')[0]
        self.favicon_path = f'home/favicons/{self.domain}.png'
        super(Source, self).save(*args, **kwargs)

    def __str__(self):
        return self.domain


class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=500)
    link = models.URLField(unique=True)
    source = models.ForeignKey(Source, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title


class List(models.Model):
    # created_by + created_at + public(bool) + Likes by user
    list_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    sources = models.ManyToManyField(Source, related_name='lists', blank=True)
    likes = models.IntegerField(default=0)

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
