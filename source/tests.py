# Django imports
from django.test import TestCase
from django.urls import reverse
from django.shortcuts import get_object_or_404
# Local imports
from home.models import Article, Source
from home.tests.test_model_instances import create_test_users, create_test_sources, create_test_sectors, create_test_website, create_test_articles, create_test_highlighted_articles, create_test_source_ratings


class SourceDetailViewTest(TestCase):
    def setUp(self):
        create_test_users()
        self.client.login(username="TestUser1", password="testpw99")
        create_test_website()
        create_test_sectors()
        create_test_sources()
        create_test_articles()
        create_test_highlighted_articles()
        create_test_source_ratings()

    def test_view(self):
        response = self.client.get(reverse('source:profile', kwargs={'slug': get_object_or_404(Source, name="TestSource1").slug}))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'source/profile.html')
        self.assertEqual(response.context['notifications_activated'], False)
        self.assertEqual(response.context['subscribed'], False)
        self.assertEqual(response.context['user_rating'], 5)
        self.assertEqual(len(response.context['latest_articles'].object_list), 5)
        self.assertEqual(response.context['latest_articles'].object_list[0], get_object_or_404(Article, title="TestArticle2"))