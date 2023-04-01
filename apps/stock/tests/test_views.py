# Django imports
from django.test import TestCase

# Local imports
from apps.tests.test_instances import CreateTestInstances


class TestStockViews(CreateTestInstances, TestCase):
    def test_portfolio_view_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/portfolio/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "stock/portfolio.html")
        self.assertEqual(response.context["selected_portfolio"].name, "Main Portfolio")
        self.assertEqual(response.context["user_portfolios"].count(), 9)

    def test_portfolio_view_anon(self):
        response = self.client.get("/portfolio/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "stock/portfolio.html")

    def test_portfolio_details_view_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/portfolio/1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "stock/portfolio.html")
        self.assertEqual(response.context["selected_portfolio"].name, "Main Portfolio")
        self.assertEqual(response.context["user_portfolios"].count(), 9)

    def test_portfolio_details_view_anon(self):
        response = self.client.get("/portfolio/1", {}, True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/login.html")

    def test_stock_view_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/stock/F")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "stock/stock_details.html")
        self.assertEqual(response.context["notification_id"], False)
        self.assertEqual(len(response.context["analysis_sources"]), 1)
        self.assertEqual(len(response.context["commentary_sources"]), 0)
        self.assertEqual(len(response.context["news_sources"]), 0)
