# Django Imports
from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.urls import reverse
# Local Imports
from apps.tests.test_model_instances import create_test_sources, create_test_sectors, create_test_website, create_test_articles
from apps.sector.models import Sector
from apps.source.models import Source 


class SectorViewTest(TestCase):
    def setUp(self):
        create_test_website()
        create_test_sectors()
        create_test_sources()

    def test_sectors(self):
        response = self.client.get(reverse('sector:sectors'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'home/sectors.html')
        self.assertEqual(Sector.objects.all().count(), 10)
        self.assertEqual(Source.objects.filter(sector = get_object_or_404(Sector, name="TestSector1")).count(), 3)


class SectorDetailViewTest(TestCase):
    def setUp(self):
        create_test_sectors()
        create_test_website()
        create_test_sources()
        create_test_articles()

    def test_sector_details(self):
        sector_slug = get_object_or_404(Sector, slug="testsector1").slug
        response = self.client.get(reverse('sector:sectors-details', kwargs={'slug': sector_slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'home/sector_details.html')
        self.assertEqual(len(response.context['articles_from_sector'].object_list), 5)
        self.assertEqual(len(response.context['tweets_from_sector'].object_list), 0)