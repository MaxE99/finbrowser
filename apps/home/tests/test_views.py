# Django imports
from django.test import TestCase

# Local imports
from apps.tests.test_instances import CreateTestInstances
from apps.home.models import NotificationMessage


class TestHomeViews(CreateTestInstances, TestCase):
    def test_notification_view_registered(self):
        self.assertEqual(
            0, NotificationMessage.objects.filter(user_has_seen=True).count()
        )
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/notifications/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/notifications.html")
        self.assertEqual(
            3, NotificationMessage.objects.filter(user_has_seen=True).count()
        )

    def test_notification_view_anon(self):
        response = self.client.get("/notifications/", {}, True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/login.html")

    def test_feed_view_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/feed.html")
        self.assertEqual(response.context["top_tweets"].count(), 1)
        self.assertEqual(response.context["latest_analysis"].count(), 5)
        self.assertEqual(response.context["latest_news"].count(), 3)
        self.assertEqual(response.context["trending_topics"].count(), 1)
        self.assertEqual(response.context["recommended_sources"].count(), 5)
        self.assertEqual(response.context["recommended_content"].count(), 7)

    def test_feed_view_anon(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/feed.html")
        self.assertEqual(response.context["top_tweets"].count(), 1)
        self.assertEqual(response.context["latest_analysis"].count(), 5)
        self.assertEqual(response.context["latest_news"].count(), 3)
        self.assertEqual(response.context["trending_topics"].count(), 1)
        self.assertEqual(response.context["recommended_sources"].count(), 5)
        self.assertEqual(response.context["recommended_content"].count(), 7)

    def test_search_results_view_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/search_results/test")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/search_results.html")
        self.assertEqual(response.context["filtered_stocks"].count(), 1)
        self.assertEqual(response.context["filtered_sources"].count(), 11)

    def test_search_results_view_anon(self):
        response = self.client.get("/search_results/test")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/search_results.html")
        self.assertEqual(response.context["filtered_stocks"].count(), 1)
        self.assertEqual(response.context["filtered_sources"].count(), 11)

    def test_not_found_view_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/somenotexistingurl/", {}, True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/feed.html")
        self.assertEqual(response.context["top_tweets"].count(), 1)
        self.assertEqual(response.context["latest_analysis"].count(), 5)
        self.assertEqual(response.context["latest_news"].count(), 3)
        self.assertEqual(response.context["trending_topics"].count(), 1)
        self.assertEqual(response.context["recommended_sources"].count(), 5)
        self.assertEqual(response.context["recommended_content"].count(), 7)

    def test_not_found_view_anon(self):
        response = self.client.get("/somenotexistingurl/", {}, True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/feed.html")
        self.assertEqual(response.context["top_tweets"].count(), 1)
        self.assertEqual(response.context["latest_analysis"].count(), 5)
        self.assertEqual(response.context["latest_news"].count(), 3)
        self.assertEqual(response.context["trending_topics"].count(), 1)
        self.assertEqual(response.context["recommended_sources"].count(), 5)
        self.assertEqual(response.context["recommended_content"].count(), 7)
