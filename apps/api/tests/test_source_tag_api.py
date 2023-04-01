# Django imports
from rest_framework.test import APITestCase

# Local imports
from apps.tests.test_instances import CreateTestInstances


class TestSourceRatingViewSet(CreateTestInstances, APITestCase):
    def test_illegal_put(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {"name": "new_name"}
        response = self.client.put("/api/source_tags/1/", data, format="json")
        self.assertEqual(response.status_code, 405)

    def test_illegal_patch(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {"name": "new_name"}
        response = self.client.patch("/api/source_tags/1/", data, format="json")
        self.assertEqual(response.status_code, 405)

    def test_illegal_destroy(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.delete("/api/source_tags/1/")
        self.assertEqual(response.status_code, 405)

    def test_illegal_post(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {"name": "new_name"}
        response = self.client.post("/api/source_tags/", data, format="json")
        self.assertEqual(response.status_code, 405)

    def test_get_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get(
            "/api/source_tags/?search_term=TestTag", format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)

    def test_get_anon(self):
        response = self.client.get(
            "/api/source_tags/?search_term=TestTag", format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)
