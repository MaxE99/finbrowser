# Django Imports
from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
# Local Imports
from apps.tests.test_model_instances import create_test_users, create_test_sources, create_test_lists, create_test_sectors, create_test_website, create_test_articles, create_test_highlighted_articles, create_test_source_ratings
from apps.article.models import Article, HighlightedArticle
from apps.list.models import List
from apps.source.models import Source

User = get_user_model()

class FeedViewTest(TestCase):
    def setUp(self):
        create_test_users()
        create_test_lists()     
        create_test_sectors() 
        create_test_website()
        create_test_sources()
        create_test_articles()
        create_test_highlighted_articles()
        get_object_or_404(Source, name="TestSource1").subscribers.add(get_object_or_404(User, username="TestUser1"))
        get_object_or_404(Source, name="TestSource2").subscribers.add(get_object_or_404(User, username="TestUser2"))
        get_object_or_404(Source, name="TestSource1").subscribers.add(get_object_or_404(User, username="TestUser2"))
        get_object_or_404(List, name="TestList1").subscribers.add(get_object_or_404(User, username="TestUser1"))
        get_object_or_404(List, name="TestList2").subscribers.add(get_object_or_404(User, username="TestUser1"))
        get_object_or_404(List, name="TestList1").subscribers.add(get_object_or_404(User, username="TestUser2"))

    def test_feed(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get(reverse('home:feed'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'home/feed.html')
        self.assertEqual(response.context['user_lists'].count(),3)
        self.assertEqual(response.context['subscribed_lists'].count(),2)
        self.assertEqual(response.context['subscribed_sources'].count(),1)
        self.assertEqual(len(response.context['subscribed_content'].object_list), 5)
        self.assertEqual(len(response.context['highlighted_content'].object_list),5)
        self.assertEqual(response.context['subscribed_content'].object_list[0], get_object_or_404(Article, title="TestArticle2"))
        self.assertEqual(response.context['highlighted_content'].object_list[0], get_object_or_404(HighlightedArticle, article=get_object_or_404(Article, title="TestArticle1"), user=get_object_or_404(User, username="TestUser1")))

    def test_feed_without_user(self):
        response = self.client.get(reverse('home:feed'))
        self.assertEqual(response.status_code,302)


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