# Django Imports
from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.timezone import now
# Python Import
from datetime import timedelta
# Local Imports
from home.models import Article, ExternalSource, HighlightedArticle, List, Notification, Sector, Source
from accounts.models import Profile
from home.tests.test_model_instances import create_test_users, create_test_sources, create_test_lists, create_test_notifications, create_test_sectors, create_test_social_links, create_test_website, create_test_list_ratings, create_test_articles, create_test_highlighted_articles

User = get_user_model()

class AddListFormTests(TestCase):
    def setUp(self):
        create_test_users()
        create_test_lists()

    def test_succesfull_list_creation(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {'name': 'TestList11', 'is_public': True}
        response = self.client.post(reverse('home:lists'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(List.objects.filter(name="TestList11").exists())

    def test_create_list_with_name_that_already_exists(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {'name': 'TestList1', 'is_public': False}
        response = self.client.post(reverse('home:lists'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(List.objects.filter(name="TestList1").count(), 1)

    def test_create_list_without_user(self):
        data = {'name': 'TestList11', 'is_public': False}
        response = self.client.post(reverse('home:lists'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(List.objects.all().count(),10)

class ListNameChangeFormTest(TestCase):
    def setUp(self):
        create_test_users()
        create_test_lists()

    def test_succesfull_list_name_change(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {'changeListForm': ['Save'], 'name': 'NewTestListName'}
        list = get_object_or_404(List, name="TestList1")
        testuser1 = get_object_or_404(Profile, user__username="TestUser1")
        response = self.client.post(reverse('home:list-details', kwargs={'profile_slug': testuser1.slug, 'list_slug':list.slug}), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(List.objects.filter(name="NewTestListName").exists())

    def test_new_listname_already_exists(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {'changeListForm': ['Save'], 'name': 'TestList3'}
        list = get_object_or_404(List, name="TestList1")
        testuser1 = get_object_or_404(Profile, user__username="TestUser1")
        response = self.client.post(reverse('home:list-details', kwargs={'profile_slug': testuser1.slug, 'list_slug':list.slug}), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(List.objects.filter(name="TestList1").exists())
        self.assertEqual(List.objects.filter(name="TestList3").count(), 1)


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
        response = self.client.get(reverse('home:articles'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'home/articles.html')
        self.assertEqual(response.context['results_found'], 10)
        self.assertEqual(response.context['articles'].count(), 10)
        self.assertEqual(len(response.context['tweets'].object_list), 0)


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


class ListsViewTest(TestCase):
    def setUp(self):
        create_test_users()
        create_test_lists()

    def test_lists(self):
        response = self.client.get(reverse('home:lists'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'home/lists.html')
        self.assertEqual(response.context['results_found'], 10)


class ListsSearchViewTest(TestCase):
    def setUp(self):
        create_test_users()
        create_test_lists()
        create_test_list_ratings()
        create_test_sectors()
        create_test_website()
        create_test_sources()

    def test_lists_search_all(self):
        response = self.client.get(reverse('home:lists-search', kwargs={'timeframe': 'All', 'content_type': 'All', 'minimum_rating': 'All', 'primary_source': 'All'}))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'home/lists.html')
        self.assertEqual(response.context['results_found'], 10)

    def test_lists_search_mixed(self):
        response = self.client.get(reverse('home:lists-search', kwargs={'timeframe': 30, 'content_type': 'All', 'minimum_rating': 2, 'primary_source': 'All'}))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'home/lists.html')
        self.assertEqual(response.context['results_found'], 3)


class SectorViewTest(TestCase):
    def setUp(self):
        create_test_website()
        create_test_sectors()
        create_test_sources()

    def test_sectors(self):
        response = self.client.get(reverse('home:sectors'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'home/sectors.html')
        self.assertEqual(Sector.objects.all().count(), 10)
        self.assertEqual(Source.objects.filter(sector = get_object_or_404(Sector, name="TestSector1")).count(), 3)


class SectorDetailViewTest(TestCase):
    def setUp(self):
        create_test_sectors()
        create_test_website()
        create_test_sources()
        create_test_articles()

    def test_sector_details(self):
        sector_slug = get_object_or_404(Sector, slug="testsector1").slug
        response = self.client.get(reverse('home:sector-details', kwargs={'slug': sector_slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'home/sector_details.html')
        self.assertEqual(len(response.context['articles_from_sector'].object_list), 5)
        self.assertEqual(len(response.context['tweets_from_sector'].object_list), 0)


class SettingsViewTest(TestCase):
    def setUp(self):
        create_test_users()
        create_test_website()
        create_test_sectors()
        create_test_social_links()
        create_test_sources()
        create_test_lists()
        create_test_notifications()

    def test_settings(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get(reverse('home:settings'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'home/settings.html')
        self.assertEqual(response.context['social_links'].count(), 5)
        self.assertEqual(response.context['notifications'].count(), 4)

    def test_settings_user_not_logged_in(self):
        response = self.client.get(reverse('home:settings'))
        self.assertEqual(response.status_code,302)


class ListDetailViewTest(TestCase):

    def setUp(self):
        create_test_users()
        create_test_website()
        create_test_sectors()
        create_test_sources()
        create_test_lists()
        create_test_list_ratings()
        create_test_articles()

    def test_list_detail(self):
        self.client.login(username="TestUser1", password="testpw99")
        list = get_object_or_404(List, name="TestList1")
        list.sources.add(get_object_or_404(Source, name="TestSource1").source_id)
        list.sources.add(get_object_or_404(Source, name="TestSource2").source_id)
        testuser1 = get_object_or_404(User, username="TestUser1")
        response = self.client.get(reverse('home:list-details', kwargs={'profile_slug': testuser1.profile.slug, 'list_slug':list.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['notifications_activated'], Notification.objects.filter(user=testuser1, list=list).exists())
        self.assertFalse(response.context['subscribed'])
        self.assertEqual(response.context['user_rating'], 3)
        self.assertEqual(response.context['list'], list)
        self.assertEqual(len(response.context['latest_articles'].object_list), 8)
        self.assertEqual(response.context['latest_articles'].object_list[0], get_object_or_404(Article, title="TestArticle2"))

    def test_notification_activated(self):
        self.client.login(username="TestUser1", password="testpw99")
        list = get_object_or_404(List, name="TestList1")
        testuser1 = get_object_or_404(User, username="TestUser1")
        Notification.objects.create(user=testuser1, list=list)
        list.subscribers.add(testuser1.id)
        response = self.client.get(reverse('home:list-details', kwargs={'profile_slug': testuser1.profile.slug, 'list_slug':list.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['notifications_activated'], Notification.objects.filter(user=testuser1, list=list).exists())
        self.assertTrue(response.context['subscribed'])


