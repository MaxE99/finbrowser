# Django imports
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
# Local imports
from home.models import Source, List, Sector


class SourceSitemap(Sitemap):

    changefreq = "hourly"
    priority = 1.0
    protocol = 'https'

    def items(self):
        return Source.objects.all()


class ListSitemap(Sitemap):

    changefreq = "hourly"
    priority = 0.9
    protocol = 'https'

    def items(self):
        return List.objects.filter(is_public=True)


class SectorSitemap(Sitemap):

    changefreq = "hourly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Sector.objects.all()


class ContentSitemaps(Sitemap):

    changefreq = "hourly"
    priority = 1.0
    protocol = 'https'

    def items(self):
        return ['home:lists', 'home:sectors', 'home:articles']

    def location(self, item):
        return reverse(item)


class HomePageSitemap(Sitemap):

    changefreq = "weekly"
    priority = 1.0
    protocol = 'https'

    def items(self):
        return ['home:main']

    def location(self, item):
        return reverse(item)