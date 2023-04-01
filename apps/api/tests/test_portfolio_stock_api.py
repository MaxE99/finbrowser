# Django imports
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail

# Local imports
from apps.tests.test_instances import CreateTestInstances
from apps.stock.models import Portfolio, PortfolioStock, Stock

User = get_user_model()


class TestPortfolioStockViewSet(CreateTestInstances, APITestCase):
    def test_post_anon(self):
        initial_ammount_of_portfolio_stocks = PortfolioStock.objects.count()
        stock = get_object_or_404(Stock, ticker="F")
        data = {"portfolio": 1, "stock": stock.pk}
        response = self.client.post("/api/portfolio_stocks/", data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )
        self.assertEqual(
            PortfolioStock.objects.count(), initial_ammount_of_portfolio_stocks
        )

    def test_post_multiple_stocks_to_portfolio_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_ammount_of_portfolio_stocks = PortfolioStock.objects.count()
        data = {"portfolio": 1, "stocks": [10, 11]}
        response = self.client.post("/api/portfolio_stocks/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            PortfolioStock.objects.count(), initial_ammount_of_portfolio_stocks + 2
        )

    def test_post_multiple_stocks_to_portfolio_to_other_user_portfolio(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {"portfolio": 10, "stocks": [10, 11]}
        response = self.client.post("/api/portfolio_stocks/", data, format="json")
        self.assertEqual(response.status_code, 404)

    def test_post_stock_to_multiple_portfolios_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_portfolio_stocks = PortfolioStock.objects.count()
        data = {"portfolios": [1, 12], "stock_id": 10}
        response = self.client.post("/api/portfolio_stocks/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(initial_portfolio_stocks + 2, PortfolioStock.objects.count())

    def test_post_stock_to_multiple_portfolios_of_other_users(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_portfolio_stocks = PortfolioStock.objects.count()
        data = {"portfolios": [10, 11], "stock_id": 10}
        response = self.client.post("/api/portfolio_stocks/", data, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(initial_portfolio_stocks, PortfolioStock.objects.count())

    def test_destroy_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_portfolio_stocks = PortfolioStock.objects.count()
        response = self.client.delete("/api/portfolio_stocks/1/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(PortfolioStock.objects.filter(pk=1).exists())
        self.assertEqual(PortfolioStock.objects.count(), initial_portfolio_stocks - 1)

    def test_destroy_other_users_portfolio_stock(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.delete("/api/portfolio_stocks/11/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            ErrorDetail(
                string="You do not have permission to perform this action.",
                code="permission_denied",
            ),
        )
        self.assertTrue(PortfolioStock.objects.filter(pk=10).exists())
        self.assertTrue(Portfolio.objects.filter(pk=10).count())

    def test_destroy_anon(self):
        initial_portfolio_stocks = PortfolioStock.objects.count()
        response = self.client.delete("/api/portfolio_stocks/1/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )
        self.assertTrue(PortfolioStock.objects.filter(pk=1).exists())
        self.assertEqual(PortfolioStock.objects.count(), initial_portfolio_stocks)

    def test_illegal_put(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {"portfolio": 5, "stock": 5}
        response = self.client.put("/api/portfolio_stocks/1/", data, format="json")
        self.assertEqual(response.status_code, 405)

    def test_illegal_patch(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {"portfolio": 5}
        response = self.client.patch("/api/portfolio_stocks/1/", data, format="json")
        self.assertEqual(response.status_code, 405)
