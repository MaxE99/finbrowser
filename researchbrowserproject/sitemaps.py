# Django imports
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

# Local imports
from apps.source.models import Source
from apps.sector.models import Sector


class RegistrationSitemaps(Sitemap):
    changefreq = "monthly"
    priority = 0.8
    protocol = "https"

    def items(self):
        return ["account_login", "account_signup"]

    def location(self, item):
        return reverse(item)


class SourceSitemap(Sitemap):

    changefreq = "hourly"
    priority = 1.0
    protocol = "https"

    def items(self):
        return Source.objects.all()


class SectorSitemap(Sitemap):

    changefreq = "hourly"
    priority = 0.8
    protocol = "https"

    def items(self):
        return Sector.objects.all()


class ContentSitemaps(Sitemap):

    changefreq = "hourly"
    priority = 1.0
    protocol = "https"

    def items(self):
        return ["list:lists", "sector:sectors", "article:articles"]

    def location(self, item):
        return reverse(item)
