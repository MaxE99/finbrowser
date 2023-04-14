# Django imports
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail

# Local imports
from apps.tests.test_instances import CreateTestInstances
from apps.list.models import List
from apps.source.models import Source
from apps.stock.models import Portfolio

User = get_user_model()


class TestSourceViewSet(CreateTestInstances, APITestCase):
    def test_illegal_post(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_ammount_of_sources = Source.objects.count()
        data = {
            "url": "https://testabcdef.com",
            "slug": "newsource",
            "name": "New Source",
            "favicon_path": "/sources/newsource",
            "paywall": "No",
            "top_source": True,
            "website": 1,
            "sector": 1,
        }
        response = self.client.post("/api/sources/", data, format="json")
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Source.objects.count(), initial_ammount_of_sources)

    def test_illegal_put(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {
            "url": "https://testabcdef.com",
            "slug": "newsource",
            "name": "New Source",
            "favicon_path": "/sources/newsource",
            "paywall": "No",
            "top_source": True,
            "website": 1,
            "sector": 1,
        }
        response = self.client.put("/api/sources/1/", data, format="json")
        self.assertEqual(response.status_code, 405)

    def test_illegal_destroy(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.delete("/api/sources/1/")
        self.assertEqual(response.status_code, 405)

    def test_get_blacklist_search_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        portfolio1 = get_object_or_404(Portfolio, name="Portfolio1")
        response = self.client.get(
            f"/api/sources/?blacklist_search=testsource&portfolio_id={portfolio1.portfolio_id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.data),
            Source.objects.filter(name__istartswith="testsource").count() - 1,
        )

    # def test_get_blacklist_search_other_user_list(self):
    #     self.client.login(username="TestUser1", password="testpw99")
    #     response = self.client.get(
    #         "/api/sources/?blacklist_search=testsource&portfolio_id=10"
    #     )
    #     self.assertEqual(response.status_code, 403)
    #     self.assertEqual(
    #         response.data,
    #         "You are not allowed to access the blacklists of other users!",
    #     )

    def test_get_blacklist_search_anon(self):
        response = self.client.get(
            "/api/sources/?blacklist_search=testsource&portfolio_id=10"
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            ErrorDetail(
                string="Authentication credentials were not provided.",
                code="not_authenticated",
            ),
        )

    def test_get_list_search_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        list1 = get_object_or_404(List, name="List1")
        response = self.client.get(
            f"/api/sources/?list_search=testsource&list_id={list1.list_id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.data),
            Source.objects.filter(name__istartswith="testsource").count() - 3,
        )

    def test_get_list_search_other_user_list(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/api/sources/?list_search=testsource&list_id=2")
        self.assertEqual(response.status_code, 404)

    def test_get_list_search_anon(self):
        response = self.client.get("/api/sources/?list_search=testsource&list_id=1")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            ErrorDetail(
                string="Authentication credentials were not provided.",
                code="not_authenticated",
            ),
        )

    def test_patch_subscription_add_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        user = get_object_or_404(User, username="TestUser1")
        source = get_object_or_404(Source, source_id=4)
        self.assertFalse(user in source.subscribers.all())
        response = self.client.patch("/api/sources/4/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(user in source.subscribers.all())

    def test_patch_subscription_remove(self):
        self.client.login(username="TestUser1", password="testpw99")
        user = get_object_or_404(User, username="TestUser1")
        source = get_object_or_404(Source, source_id=1)
        self.assertTrue(user in source.subscribers.all())
        response = self.client.patch("/api/sources/1/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(user in source.subscribers.all())

    def test_patch_subscription_add_anon(self):
        response = self.client.patch("/api/sources/1/")
        self.assertEqual(response.status_code, 403)

    def test_illegal_patches(self):
        self.client.login(username="TestUser1", password="testpw99")
        source = get_object_or_404(Source, source_id=1)
        data = {"url": "https://www.google.com/"}
        response = self.client.patch("/api/sources/1/", data, format="json")
        self.assertEqual(response.status_code, 200)
        source.refresh_from_db()
        self.assertNotEqual(source.url, "https://www.google.com/")

    def test_get_subs_search_anon(self):
        response = self.client.get("/api/sources/?subs_search=Test")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            ErrorDetail(
                string="Authentication credentials were not provided.",
                code="not_authenticated",
            ),
        )

    def test_get_subs_search_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/api/sources/?subs_search=Test")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 8)
