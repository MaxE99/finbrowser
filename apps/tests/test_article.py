# Django Imports
from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
# Python Import
from datetime import timedelta
# Local Imports
from apps.tests.test_model_instances import create_test_users, create_test_sources, create_test_lists, create_test_sectors, create_test_website, create_test_articles
from apps.article.models import Article, HighlightedArticle
from apps.sector.models import Sector
from apps.source.models import ExternalSource

class AddExternalArticlesFormTests(TestCase):
    def setUp(self):
        create_test_users()
        self.client.login(username="TestUser1", password="testpw99")
        create_test_lists()     
        create_test_sectors()  

    def test_succesfullly_created_external_article(self):
        data = {'addExternalArticlesForm': ['Save'], 'website_name': 'TestWebsite', 'sector': get_object_or_404(Sector, name="TestSector1").sector_id, 'title': 'TestArticleTitle', 'link': 'https://testwebsite.com', 'pub_date': (now() - timedelta(days=3)).strftime("%Y-%m-%d")}
        response = self.client.post(reverse('home:feed'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ExternalSource.objects.filter(website_name="TestWebsite").exists())
        self.assertTrue(Article.objects.filter(title="TestArticleTitle").exists())
        self.assertTrue(HighlightedArticle.objects.filter(article=get_object_or_404(Article, title="TestArticleTitle")).exists())


class ArticleViewTest(TestCase):
    def setUp(self):
        create_test_sectors()
        create_test_website()
        create_test_sources()
        create_test_articles()

    def test_articles(self):
        response = self.client.get(reverse('article:articles'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'article/articles.html')
        self.assertEqual(response.context['results_found'], 10)
        self.assertEqual(len(response.context['articles']), 10)
        self.assertEqual(len(response.context['tweets'].object_list), 0)