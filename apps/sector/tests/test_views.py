# Django imports
from django.test import TestCase

# Local imports
from apps.tests.test_instances import CreateTestInstances


class TestSectorViews(CreateTestInstances, TestCase):
    def test_sector_detail_view_(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/sector/testsector1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "sector/sector_details.html")
        self.assertEqual(response.context["analysis_sources"].count(), 1)
        self.assertEqual(response.context["commentary_sources"].count(), 1)
        self.assertEqual(response.context["news_sources"].count(), 1)
