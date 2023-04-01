# Django imports
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail


# Local imports
from apps.tests.test_instances import CreateTestInstances
from apps.article.models import Article, HighlightedArticle

User = get_user_model()


class TestHighlightedArticlesViewSet(CreateTestInstances, APITestCase):
    def test_illegal_put(self):
        self.client.login(username="TestUser1", password="testpw99")
        new_user = get_object_or_404(User, username="TestUser2")
        new_article = get_object_or_404(Article, pk=8)
        data = {"user": new_user.pk, "article": new_article.pk}
        response = self.client.put("/api/highlighted_articles/1/", data, format="json")
        self.assertEqual(response.status_code, 405)

    def test_illegal_patch(self):
        self.client.login(username="TestUser1", password="testpw99")
        new_article = get_object_or_404(Article, pk=8)
        data = {"article": new_article.pk}
        response = self.client.patch(
            "/api/highlighted_articles/1/", data, format="json"
        )
        self.assertEqual(response.status_code, 405)

    def test_illegal_destroy(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.delete("/api/highlighted_articles/1/")
        self.assertEqual(response.status_code, 405)

    def test_post_anon(self):
        new_user = get_object_or_404(User, username="TestUser2")
        new_article = get_object_or_404(Article, pk=8)
        data = {"user": new_user.pk, "article": new_article.pk}
        response = self.client.put("/api/highlighted_articles/1/", data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            ErrorDetail(
                string="Authentication credentials were not provided.",
                code="not_authenticated",
            ),
        )

    def test_post_registered_unhighlight(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_highlighted_articles = HighlightedArticle.objects.count()
        data = {"article": 1}
        response = self.client.post("/api/highlighted_articles/", data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(HighlightedArticle.objects.filter(pk=1).count())
        self.assertEqual(
            initial_highlighted_articles, HighlightedArticle.objects.count() + 1
        )

    def test_post_registered_highlight(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_highlighted_articles = HighlightedArticle.objects.count()
        data = {"article": 10}
        response = self.client.post("/api/highlighted_articles/", data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            initial_highlighted_articles, HighlightedArticle.objects.count() - 1
        )
