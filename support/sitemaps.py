from django.contrib.sitemaps import Sitemap
from django.urls import reverse


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