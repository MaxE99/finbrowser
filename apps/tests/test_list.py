# Django Imports
from django.shortcuts import get_object_or_404
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
# Local Imports
from apps.tests.test_model_instances import create_test_users, create_test_sources, create_test_lists, create_test_sectors, create_test_website, create_test_articles, create_test_list_ratings
from apps.article.models import Article
from apps.list.models import List
from apps.accounts.models import Profile
from apps.source.models import Source
from apps.home.models import Notification

User = get_user_model()

class ListsViewTest(TestCase):
    def setUp(self):
        create_test_users()
        create_test_lists()

    def test_lists(self):
        response = self.client.get(reverse('list:lists'))
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
        response = self.client.get(reverse('list:lists-search', kwargs={'timeframe': 'All', 'content_type': 'All', 'minimum_rating': 'All', 'primary_source': 'All'}))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'home/lists.html')
        self.assertEqual(response.context['results_found'], 10)

    def test_lists_search_mixed(self):
        response = self.client.get(reverse('list:lists-search', kwargs={'timeframe': 30, 'content_type': 'All', 'minimum_rating': 2, 'primary_source': 'All'}))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'home/lists.html')
        self.assertEqual(response.context['results_found'], 3)


class AddListFormTests(TestCase):
    def setUp(self):
        create_test_users()
        create_test_lists()

    def test_succesfull_list_creation(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {'name': 'TestList11', 'is_public': True}
        response = self.client.post(reverse('list:lists'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(List.objects.filter(name="TestList11").exists())

    def test_create_list_with_name_that_already_exists(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {'name': 'TestList1', 'is_public': False}
        response = self.client.post(reverse('list:lists'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(List.objects.filter(name="TestList1").count(), 1)

    def test_create_list_without_user(self):
        data = {'name': 'TestList11', 'is_public': False}
        response = self.client.post(reverse('list:lists'), data)
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
        response = self.client.post(reverse('list:lists-details', kwargs={'profile_slug': testuser1.slug, 'list_slug':list.slug}), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(List.objects.filter(name="NewTestListName").exists())

    def test_new_listname_already_exists(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {'changeListForm': ['Save'], 'name': 'TestList3'}
        list = get_object_or_404(List, name="TestList1")
        testuser1 = get_object_or_404(Profile, user__username="TestUser1")
        response = self.client.post(reverse('list:lists-details', kwargs={'profile_slug': testuser1.slug, 'list_slug':list.slug}), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(List.objects.filter(name="TestList1").exists())
        self.assertEqual(List.objects.filter(name="TestList3").count(), 1)



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
        response = self.client.get(reverse('list:lists-details', kwargs={'profile_slug': testuser1.profile.slug, 'list_slug':list.slug}))
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
        response = self.client.get(reverse('list:lists-details', kwargs={'profile_slug': testuser1.profile.slug, 'list_slug':list.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['notifications_activated'], Notification.objects.filter(user=testuser1, list=list).exists())
        self.assertTrue(response.context['subscribed'])