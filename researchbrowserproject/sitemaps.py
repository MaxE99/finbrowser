# Django imports
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

# Local imports
from apps.source.models import Source
from apps.sector.models import Sector
from apps.stock.models import Stock


class RegistrationSitemaps(Sitemap):
    changefreq = "monthly"
    priority = 0.6
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

    def location(self, obj):
        return reverse("source:source_profile", args=[obj.slug])


class StockSitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.9
    protocol = "https"

    def items(self):
        return Stock.objects.all()

    def location(self, obj):
        return reverse("stock:stock-details", args=[obj.ticker])


class SectorSitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.8
    protocol = "https"

    def items(self):
        return Sector.objects.all()

    def location(self, obj):
        return reverse("sector:sector-details", args=[obj.slug])


class ContentSitemaps(Sitemap):
    changefreq = "hourly"
    priority = 0.9
    protocol = "https"

    def items(self):
        return ["home:feed", "home:guide", "source:source_ranking"]

    def location(self, item):
        return reverse(item)
