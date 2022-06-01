# Django imports
from django.test import TestCase
from django.urls import reverse
from django.shortcuts import get_object_or_404
# Local imports
from accounts.models import Website
from home.models import Sector, Source

class ProfileViewTest(TestCase):
    def setUp(self):
        website = Website.objects.create(name="Substack")
        sector = Sector.objects.create(name="Short", slug="short")
        Source.objects.create(url="https://doomberg.substack.com/", slug="doomberg", name="Doomberg", paywall="Yes", website=website, sector=sector)

    def test_view(self):
        response = self.client.get(reverse('source:profile', kwargs={'slug': get_object_or_404(Source, slug="doomberg").slug}))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'source/profile.html')