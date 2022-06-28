# Django imports
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
# Local imports
from apps.accounts.models import Profile
from apps.source.models import Source
from apps.sector.models import Sector
from apps.list.models import List

class SupportSitemaps(Sitemap):

    changefreq = "monthly"
    priority = 0.2
    protocol = 'https'

    def items(self):
        return [
            'support:faq', 'support:report-bug', 'support:suggestions',
            'support:privacy-policy', 'support:cookie-statement',
            'support:terms-of-service', 'support:suggest-sources',
            'support:about', 'support:sitemap'
        ]

    def location(self, item):
        return reverse(item)


class ProfileSitemap(Sitemap):

    changefreq = "daily"
    priority = 0.5
    protocol = 'https'

    def items(self):
        return Profile.objects.all()


class RegistrationSitemaps(Sitemap):
    changefreq = "monthly"
    priority = 0.4
    protocol = 'https'

    def items(self):
        return ['account_login', 'account_signup']

    def location(self, item):
        return reverse(item)


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
        return ['list:lists', 'sector:sectors', 'article:articles']

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