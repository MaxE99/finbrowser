# Django imports
from rest_framework.test import APITestCase

# Python imports
import json

# Local imports
from apps.tests.test_instances import CreateTestInstances


class TestFilteredSiteViewSet(CreateTestInstances, APITestCase):
    def test_get_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/api/search_site/Test", format="json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data[0]), 1)
        self.assertEqual(len(data[1]), 7)
        self.assertEqual(len(data[2]), 1)

    def test_get_anon(self):
        response = self.client.get("/api/search_site/Test", format="json")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data[0]), 1)
        self.assertEqual(len(data[1]), 7)
        self.assertEqual(len(data[2]), 1)
