# Django imports
from rest_framework.test import APITestCase

# Local imports
from apps.tests.test_instances import CreateTestInstances


class TestStockViewSet(CreateTestInstances, APITestCase):
    def test_illegal_put(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {
            "ticker": "ABCD",
            "full_company_name": "TestCompany",
            "short_company_name": "TestCompany",
        }
        response = self.client.put("/api/stocks/1/", data, format="json")
        self.assertEqual(response.status_code, 405)

    def test_illegal_patch(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {
            "ticker": "ABCD",
            "full_company_name": "TestCompany",
            "short_company_name": "TestCompany",
        }
        response = self.client.patch("/api/stocks/1/", data, format="json")
        self.assertEqual(response.status_code, 405)

    def test_illegal_destroy(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.delete("/api/stocks/1/")
        self.assertEqual(response.status_code, 405)

    def test_illegal_post(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {
            "ticker": "ABCD",
            "full_company_name": "TestCompany",
            "short_company_name": "TestCompany",
        }
        response = self.client.post("/api/stocks/", data, format="json")
        self.assertEqual(response.status_code, 405)

    def test_get_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/api/stocks/?search_term=Test", format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_anon(self):
        response = self.client.get("/api/stocks/?search_term=Test", format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
