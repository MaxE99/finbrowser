# Django imports
from django.test import TestCase

# Local imports
from apps.tests.test_instances import CreateTestInstances


class TestListViews(CreateTestInstances, TestCase):
    def test_highlighted_content_view_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/list/highlighted_content")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "list/highlighted_content_list.html")
        self.assertEqual(response.context["lists"].count(), 8)

    def test_highlighted_content_view_anon(self):
        response = self.client.get("/list/highlighted_content", {}, True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/login.html")

    def test_subscribed_content_view_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/list/subscribed_sources")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "list/subscribed_sources_list.html")
        self.assertEqual(response.context["lists"].count(), 8)
        self.assertEqual(response.context["analysis_sources"].count(), 1)
        self.assertEqual(response.context["commentary_sources"].count(), 1)
        self.assertEqual(response.context["news_sources"].count(), 1)

    def test_subscribed_content_view_anon(self):
        response = self.client.get("/list/subscribed_sources", {}, True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/login.html")

    def test_lists_view_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/lists")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "list/list_details.html")
        self.assertEqual(response.context["lists"].count(), 8)
        self.assertEqual(response.context["list"].name, "Main List")

    def test_lists_view_anon(self):
        response = self.client.get("/lists")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "list/list_details.html")

    def test_lists_details_view_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/list/1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "list/list_details.html")
        self.assertEqual(response.context["lists"].count(), 8)
        self.assertEqual(response.context["list"].name, "Main List")

    def test_lists_view_anon(self):
        response = self.client.get("/list/1", {}, True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/login.html")
