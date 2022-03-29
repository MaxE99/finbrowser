# Django imports
from django.db import models
# Python imports
from operator import itemgetter
# Local imports
from home.logic.scrapper import website_scrapping_initiate


class Source(models.Model):
    PAYWALL_CHOICES = [('Yes', 'Yes'), ('Semi', 'Semi'), ('No', 'No')]
    WEBSITE_CHOICES = [('Medium', 'Medium'), ('Other', 'Other'),
                       ('SeekingAlpha', 'SeekingAlpha'),
                       ('Substack', 'Substack'), ('Twitter', 'Twitter'),
                       ('YouTube', 'YouTube')]
    source_id = models.AutoField(primary_key=True)
    url = models.URLField(unique=True)
    domain = models.CharField(max_length=100, blank=True)
    favicon_path = models.CharField(max_length=500, blank=True)
    paywall = models.CharField(max_length=10,
                               choices=PAYWALL_CHOICES,
                               default='None')
    website = models.CharField(max_length=100,
                               choices=WEBSITE_CHOICES,
                               default='None')

    def save(self, *args, **kwargs):
        self.domain = self.url.replace("https://",
                                       "").replace("www.", "").split('.')[0]
        self.favicon_path = f'home/favicons/{self.domain}.png'
        website_scrapping_initiate(self.url, self.domain)
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
    CONTENT_CHOICES = [('Articles', 'Articles'), ('Sources', 'Sources')]
    # created_by + created_at + public(bool) + Likes by user
    list_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    content_type = models.CharField(max_length=10,
                                    choices=CONTENT_CHOICES,
                                    default='None')
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.IntegerField(default=0)
    sources = models.ManyToManyField(Source, related_name='lists', blank=True)
    main_website_source = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        # If more than 50% of websites are from one source, then set main_website_source to this source
        list = List.objects.get(list_id=self.list_id)
        websites = [["Medium", 0], ["Other", 0], ["SeekingAlpha", 0],
                    ["Substack", 0], ["Twitter", 0], ["YouTube", 0]]
        for source in list.sources.all():
            for website in websites:
                if source.website == website[0]:
                    website[1] += 1
                    break
        websites = sorted(websites, key=itemgetter(1), reverse=True)
        if (websites[0][1] / len(list.sources.all())) * 100 >= 50:
            self.main_website_source = websites[0][0]
        super(List, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


# 1.Zu jedem List-Objekt will ich speichern wie viel Prozent Quellen zu entsprechenden Webseiten sind
# Möglichkeiten:
# 1.Ich mach das ganze als Property und berechne es als Property jedes mal bei Abfrage
# => beschissene Idee: So müsste ich jedes mal für jede Liste ne Berechnung durchführen, wenn jemand eine Filtersuche macht
# 2.Ich muss also sehen, dass ich diese Berechnung jedes mal mache, wenn die List geupdated wird
# Neue Idee:
# Char Feld in dem ich Namen der Webseite abspeichere, wenn eine Quelle über 50% ausmacht, ansonsten lasse ich leer
# Bei jedem speichern in save() Methode überprüfen ob eine Quelle mehr als 50% ausmacht und wenn ja Namen der Webseite abspeichern


class Sector(models.Model):
    list_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
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
