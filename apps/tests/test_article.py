# Django Imports
from django.test import TestCase
from django.urls import reverse

# Local Imports
from apps.tests.test_model_instances import create_test_users, create_test_sources, create_test_lists, create_test_sectors, create_test_website, create_test_articles

class AddExternalArticlesFormTests(TestCase):
    def setUp(self):
        create_test_users()
        self.client.login(username="TestUser1", password="testpw99")
        create_test_lists()     
        create_test_sectors()  
        

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