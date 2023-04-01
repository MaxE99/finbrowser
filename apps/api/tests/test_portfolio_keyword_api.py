# Django imports
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail

# Local imports
from apps.tests.test_instances import CreateTestInstances
from apps.stock.models import PortfolioKeyword

User = get_user_model()


class TestPortfolioKeywordViewSet(CreateTestInstances, APITestCase):
    def test_post_anon(self):
        initial_keywords = PortfolioKeyword.objects.count()
        data = {"keyword": "This is a new keyword", "pstock_id": 1}
        response = self.client.post("/api/portfolio_keywords/", data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )
        self.assertEqual(PortfolioKeyword.objects.count(), initial_keywords)

    def test_post_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_keywords = PortfolioKeyword.objects.count()
        initial_keywords_from_stock = (
            get_object_or_404(PortfolioKeyword, pk=1)
            .portfolio_stocks.all()
            .first()
            .keywords.all()
            .count()
        )
        data = {"keyword": "This is a new keyword", "pstock_id": 1}
        response = self.client.post("/api/portfolio_keywords/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(PortfolioKeyword.objects.count(), initial_keywords + 1)
        self.assertEqual(
            get_object_or_404(PortfolioKeyword, pk=1)
            .portfolio_stocks.all()
            .first()
            .keywords.all()
            .count(),
            initial_keywords_from_stock + 1,
        )

    def test_destroy_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_keywords = PortfolioKeyword.objects.count()
        response = self.client.delete("/api/portfolio_keywords/1/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(PortfolioKeyword.objects.filter(pk=1).exists())
        self.assertEqual(PortfolioKeyword.objects.count(), initial_keywords - 1)

    def test_destroy_other_users_portfolio_keyword(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_keywords = PortfolioKeyword.objects.count()
        response = self.client.delete("/api/portfolio_keywords/11/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            ErrorDetail(
                string="You do not have permission to perform this action.",
                code="permission_denied",
            ),
        )
        self.assertTrue(PortfolioKeyword.objects.filter(pk=11).exists())
        self.assertEqual(PortfolioKeyword.objects.count(), initial_keywords)

    def test_destroy_anon(self):
        initial_keywords = PortfolioKeyword.objects.count()
        response = self.client.delete("/api/portfolio_keywords/1/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )
        self.assertTrue(PortfolioKeyword.objects.filter(pk=1).exists())
        self.assertEqual(PortfolioKeyword.objects.count(), initial_keywords)

    def test_illegal_put(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {"keyword": "New Keyword"}
        response = self.client.put("/api/portfolio_keywords/1/", data, format="json")
        self.assertEqual(response.status_code, 405)

    def test_illegal_patch(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {"keyword": "New Keyword"}
        response = self.client.patch("/api/portfolio_keywords/1/", data, format="json")
        self.assertEqual(response.status_code, 405)
