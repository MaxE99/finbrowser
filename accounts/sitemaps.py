# Django imports
from django.contrib.sitemaps import Sitemap
# Local imports
from accounts.models import Profile


class ProfileSitemap(Sitemap):

    changefreq = "daily"
    priority = 0.5
    protocol = 'https'

    def items(self):
        return Profile.objects.all()
