# Django imports
from rest_framework.test import APITestCase

# Local imports
from apps.tests.test_instances import CreateTestInstances


class TestArticleViewSet(CreateTestInstances, APITestCase):
    def test_get_best_content_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/api/articles/?feed_content=0", format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 9)

    def test_get_best_content_anon(self):
        response = self.client.get("/api/articles/?feed_content=0", format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 9)

    def test_get_best_tweets_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/api/articles/?best_tweets=0", format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_best_tweets_anon(self):
        response = self.client.get("/api/articles/?best_tweets=0", format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
