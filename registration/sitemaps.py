## Django imports
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class RegistrationSitemaps(Sitemap):

    changefreq = "monthly"
    priority = 0.4
    protocol = 'https'

    def items(self):
        return ['registration:login', 'registration:register']

    def location(self, item):
        return reverse(item)
