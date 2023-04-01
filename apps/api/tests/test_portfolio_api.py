# Django imports
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail

# Local imports
from apps.tests.test_instances import CreateTestInstances
from apps.stock.models import Portfolio

User = get_user_model()


class TestPortfolioViewSet(CreateTestInstances, APITestCase):
    def test_post_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_ammount_of_portfolios = Portfolio.objects.count()
        response = self.client.post("/api/portfolios/")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Portfolio.objects.count(), initial_ammount_of_portfolios + 1)

    def test_post_anon(self):
        initial_ammount_of_portfolios = Portfolio.objects.count()
        response = self.client.post("/api/portfolios/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )
        self.assertEqual(Portfolio.objects.count(), initial_ammount_of_portfolios)

    def test_destroy_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        user = get_object_or_404(User, username="TestUser1")
        main_list = get_object_or_404(Portfolio, user=user, main=True)
        response = self.client.delete("/api/portfolios/1/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Portfolio.objects.filter(pk=1).count())
        self.assertNotEqual(
            main_list, get_object_or_404(Portfolio, user=user, main=True)
        )
        self.assertTrue(Portfolio.objects.filter(main=True, user=user).count())

    def test_destroy_other_users_portfolio(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.delete("/api/portfolios/8/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            ErrorDetail(
                string="You do not have permission to perform this action.",
                code="permission_denied",
            ),
        )
        self.assertTrue(Portfolio.objects.filter(pk=8).count())

    def test_destroy_anon(self):
        response = self.client.delete("/api/portfolios/1/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )
        self.assertTrue(Portfolio.objects.filter(pk=1).count())

    def test_destroy_last_portfolio(self):
        self.client.login(username="TestUser12", password="testpw99")
        user = get_object_or_404(User, username="TestUser12")
        response = self.client.delete("/api/portfolios/11/")
        self.assertFalse(Portfolio.objects.filter(pk=11).count())
        last_portfolio = get_object_or_404(Portfolio, user=user)
        response = self.client.delete(f"/api/portfolios/${last_portfolio.pk}/")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data, "You are not allowed to delete your last portfolio!"
        )
        self.assertTrue(Portfolio.objects.filter(user=user).count())

    def test_illegal_put(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {
            "user": 3,
            "name": "New Portfolio",
            "main": True,
        }
        response = self.client.put("/api/portfolios/1/", data, format="json")
        self.assertEqual(response.status_code, 405)

    def test_patch_name_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {"name": "new_name"}
        response = self.client.patch("/api/portfolios/1/", data=data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(Portfolio, pk=1).name, "new_name")

    def test_patch_name_of_other_users_list(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_portfolio_name = get_object_or_404(Portfolio, pk=11).name
        data = {"name": "new_name"}
        response = self.client.patch("/api/portfolios/11/", data=data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            ErrorDetail(
                string="You do not have permission to perform this action.",
                code="permission_denied",
            ),
        )
        self.assertEqual(
            get_object_or_404(Portfolio, pk=11).name, initial_portfolio_name
        )

    def test_patch_name_anon(self):
        initial_portfolio_name = get_object_or_404(Portfolio, pk=1).name
        data = {"name": "new_name"}
        response = self.client.patch("/api/portfolios/1/", data=data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )
        self.assertEqual(
            get_object_or_404(Portfolio, pk=1).name, initial_portfolio_name
        )

    def test_patch_add_to_blacklist(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {"source_id": 10}
        initial_blacklist = (
            get_object_or_404(Portfolio, pk=1).blacklisted_sources.all().count()
        )
        response = self.client.patch("/api/portfolios/1/", data=data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            initial_blacklist + 1,
            get_object_or_404(Portfolio, pk=1).blacklisted_sources.all().count(),
        )

    def test_illegal_patch_add_source_to_other_users_blacklist(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {"source_id": 10}
        initial_blacklist = (
            get_object_or_404(Portfolio, pk=2).blacklisted_sources.all().count()
        )
        response = self.client.patch("/api/portfolios/2/", data=data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            initial_blacklist,
            get_object_or_404(Portfolio, pk=2).blacklisted_sources.all().count(),
        )

    # def test_illegal_patch_user(self): # throws db integrity error
    #     self.client.login(username="TestUser1", password="testpw99")
    #     data = {"user": 2}
    #     response = self.client.patch("/api/portfolios/1/", data=data, format="json")
    #     self.assertEqual(response.status_code, 403)
