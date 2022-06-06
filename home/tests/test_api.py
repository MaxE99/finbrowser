# Django Imports
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
# Local Imports
from home.models import Article, HighlightedArticle, List, ListRating, Notification, Source, SourceRating
from accounts.models import SocialLink, Website
from home.tests.test_model_instances import create_test_source_ratings, create_test_users, create_test_sources, create_test_lists, create_test_notifications, create_test_sectors, create_test_social_links, create_test_website, create_test_list_ratings, create_test_articles

User = get_user_model()

class HighlightedArticleViewSetTest(APITestCase):

    def setUp(self):
        create_test_users()
        self.client.login(username="TestUser1", password="testpw99")
        create_test_website()
        create_test_sectors()
        create_test_sources()
        create_test_articles()

    def test_change_highlighted_articles_status(self):
        article = get_object_or_404(Article, title="TestArticle1")
        data = {"article_id": article.article_id}
        self.assertFalse(HighlightedArticle.objects.filter(user=get_object_or_404(User, username="TestUser1"), article=article).exists())
        self.client.post("/api/highlighted_articles/", data)
        self.assertTrue(HighlightedArticle.objects.filter(user=get_object_or_404(User, username="TestUser1"), article=article).exists())


class SocialLinkViewSetTest(APITestCase):

    def setUp(self):
        create_test_users()
        self.client.login(username="TestUser1", password="testpw99")
        create_test_website()
        create_test_sectors()
        create_test_sources()
        create_test_articles()
        create_test_social_links()

    def test_create_social_links(self):
        data = {"website": get_object_or_404(Website, name="TestWebsite1").id, "url": "www.newtestlink.com"}
        self.assertFalse(SocialLink.objects.filter(url="www.newtestlink.com").exists())
        self.client.post(f"/api/social_links/", data)
        self.assertTrue(SocialLink.objects.filter(url="www.newtestlink.com").exists())

    def test_update_social_links(self):
        data = {"website": get_object_or_404(Website, name="TestWebsite4").id, "url": "www.newtestlink.com"}
        social_link = get_object_or_404(SocialLink, url="www.website/testuser1.com")
        self.assertFalse(SocialLink.objects.filter(url="www.newtestlink.com").exists())
        self.client.put(f"/api/social_links/{social_link.id}/", data)
        self.assertTrue(SocialLink.objects.filter(url="www.newtestlink.com").exists())

    def test_try_updating_other_users_social_links(self):
        data = {"website": get_object_or_404(Website, name="TestWebsite8").id, "url": "www.newtestlink.com"}
        social_link = get_object_or_404(SocialLink, url="www.website/testuser10.com")
        self.client.put(f"/api/social_links/{social_link.id}/", data)
        self.assertFalse(SocialLink.objects.filter(url="www.newtestlink.com").exists())
        self.assertTrue(SocialLink.objects.filter(url="www.website/testuser10.com").exists())

    def test_delete_social_links(self):
        social_link = get_object_or_404(SocialLink, url="www.website/testuser1.com")
        self.client.delete(f"/api/social_links/{social_link.id}/")
        self.assertFalse(SocialLink.objects.filter(url="www.website/testuser1.com").exists())
        self.assertEqual(SocialLink.objects.all().count(),9)

    def test_try_deleting_other_users_social_links(self):
        social_link = get_object_or_404(SocialLink, url="www.website/testuser10.com")
        self.client.delete(f"/api/social_links/{social_link.id}/")
        self.assertTrue(SocialLink.objects.filter(url="www.website/testuser10.com").exists())
        self.assertEqual(SocialLink.objects.all().count(),10)


class SourceRatingViewSetTest(APITestCase):

    def setUp(self):
        create_test_users()
        create_test_website()
        create_test_sectors()
        create_test_sources()

    def test_rating_without_login(self):
        data = {"source_id": get_object_or_404(Source, name="TestSource1").source_id, "rating": 4}
        self.client.post("/api/source_ratings/", data)
        self.assertEqual(SourceRating.objects.all().count(), 0)

    def test_adding_new_rating(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {"source_id": get_object_or_404(Source, name="TestSource1").source_id, "rating": 4}
        self.client.post("/api/source_ratings/", data)
        self.assertEqual(SourceRating.objects.all().count(), 1)
        self.assertEqual(SourceRating.objects.get(source=get_object_or_404(Source, name="TestSource1")).rating, 4)

    def test_change_rating(self):
        self.client.login(username="TestUser1", password="testpw99")
        create_test_source_ratings()
        data = {"source_id": get_object_or_404(Source, name="TestSource1").source_id, "rating": 2}
        self.client.post("/api/source_ratings/", data)
        self.assertEqual(SourceRating.objects.all().count(), 10)
        self.assertEqual(get_object_or_404(SourceRating, source=get_object_or_404(Source, name="TestSource1"), user=get_object_or_404(User, username="TestUser1")).rating, 2)
        self.assertEqual(SourceRating.objects.get_average_rating(get_object_or_404(Source, name="TestSource1")), 2)
        self.assertEqual(SourceRating.objects.get_ammount_of_ratings(get_object_or_404(Source, name="TestSource1")), 4)


class ListRatingViewSetTest(APITestCase):

    def setUp(self):
        create_test_users()
        create_test_lists()

    def test_rating_without_login(self):
        data = {"list_id": get_object_or_404(List, name="TestList1").list_id, "rating": 4}
        self.client.post("/api/list_ratings/", data)
        self.assertEqual(ListRating.objects.all().count(), 0)

    def test_adding_new_rating(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {"list_id": get_object_or_404(List, name="TestList1").list_id, "rating": 4}
        self.client.post("/api/list_ratings/", data)
        self.assertEqual(ListRating.objects.all().count(), 1)
        self.assertEqual(ListRating.objects.get(list=get_object_or_404(List, name="TestList1")).rating, 4)

    def test_change_rating(self):
        self.client.login(username="TestUser1", password="testpw99")
        create_test_list_ratings()
        data = {"list_id": get_object_or_404(List, name="TestList1").list_id, "rating": 2}
        self.client.post("/api/list_ratings/", data)
        self.assertEqual(ListRating.objects.all().count(), 10)
        self.assertEqual(get_object_or_404(ListRating, list=get_object_or_404(List, name="TestList1"), user=get_object_or_404(User, username="TestUser1")).rating, 2)
        self.assertEqual(ListRating.objects.get_average_rating(get_object_or_404(List, name="TestList1")), 3.3)
        self.assertEqual(ListRating.objects.get_ammount_of_ratings(get_object_or_404(List, name="TestList1")), 6)


class SourceViewSetTest(APITestCase):

    def setUp(self):
        create_test_users()
        self.client.login(username="TestUser1", password="testpw99")
        create_test_website()
        create_test_sectors()
        create_test_sources()
        create_test_lists()

    def test_change_subscribtion_status(self):
        source_id = get_object_or_404(Source, name="TestSource1").source_id
        self.client.post(f"/api/sources/{source_id}/source_change_subscribtion_status/")
        self.assertTrue(get_object_or_404(Source, name="TestSource1").subscribers.filter(username=get_object_or_404(User, username="TestUser1").username).exists())  
        self.client.post(f"/api/sources/{source_id}/source_change_subscribtion_status/")
        self.assertFalse(get_object_or_404(Source, name="TestSource1").subscribers.filter(username=get_object_or_404(User, username="TestUser1").username).exists())          

    def test_list_feed_search(self):
        testlist1 = get_object_or_404(List, name="TestList1")
        testlist1.sources.add(get_object_or_404(Source, name="TestSource1"))
        testlist1.sources.add(get_object_or_404(Source, name="TestSource2"))
        testlist1.sources.add(get_object_or_404(Source, name="TestSource3"))
        response = self.client.get(f"/api/sources/?list_search=TestSource&list_id={testlist1.list_id}")   
        self.assertEqual(len(response.data), 7)

    def test_list_feed_search_with_other_users_list(self):
        testlist2 = get_object_or_404(List, name="TestList2")
        testlist2.sources.add(get_object_or_404(Source, name="TestSource1"))
        testlist2.sources.add(get_object_or_404(Source, name="TestSource2"))
        testlist2.sources.add(get_object_or_404(Source, name="TestSource3"))
        response = self.client.get(f"/api/sources/?list_search=TestSource&list_id={testlist2.list_id}")   
        self.assertEqual(len(response.data), 0)
    
    def test_source_feed_search(self):
        source_id1 = get_object_or_404(Source, name="TestSource1").source_id
        source_id2 = get_object_or_404(Source, name="TestSource2").source_id
        self.client.post(f"/api/sources/{source_id1}/source_change_subscribtion_status/")      
        self.client.post(f"/api/sources/{source_id2}/source_change_subscribtion_status/")      
        response = self.client.get(f"/api/sources/?feed_search=TestSource")
        self.assertEqual(len(response.data), 8)


class ListViewSetTest(APITestCase):

    def setUp(self):
        create_test_users()
        self.client.login(username="TestUser1", password="testpw99")
        create_test_website()
        create_test_sectors()
        create_test_sources()
        create_test_lists()
        create_test_articles()

    def test_delete_list(self):
        self.assertEqual(List.objects.filter(name="TestList1").count(), 1)
        list = get_object_or_404(List, name="TestList1")
        self.client.delete(f"/api/lists/{list.list_id}/")
        self.assertEqual(List.objects.filter(name="TestList1").count(), 0)

    def test_try_to_delete_other_users_list(self):
        self.assertEqual(List.objects.filter(name="TestList2").count(), 1)
        list = get_object_or_404(List, name="TestList2")
        self.client.delete(f"/api/lists/{list.list_id}/")
        self.assertEqual(List.objects.filter(name="TestList2").count(), 1)

    def test_change_list_subscribtion(self):
        list = get_object_or_404(List, name="TestList2")
        self.client.post(f"/api/lists/{list.list_id}/list_change_subscribtion_status/")
        self.assertTrue(get_object_or_404(List, name="TestList2").subscribers.filter(username=get_object_or_404(User, username="TestUser1").username).exists()) 
        self.client.post(f"/api/lists/{list.list_id}/list_change_subscribtion_status/")
        self.assertFalse(get_object_or_404(List, name="TestList2").subscribers.filter(username=get_object_or_404(User, username="TestUser1").username).exists())

    def test_delete_source_from_list(self):
        list = get_object_or_404(List, name="TestList1")
        list.sources.add(get_object_or_404(Source, name="TestSource1"))
        list.sources.add(get_object_or_404(Source, name="TestSource2"))
        source = get_object_or_404(Source, name="TestSource1")
        self.assertTrue(list.sources.filter(source_id=source.source_id).exists())
        self.client.delete(f"/api/lists/{list.list_id}/delete_source_from_list/{source.source_id}/")
        self.assertFalse(list.sources.filter(source_id=source.source_id).exists())

    def test_try_to_delete_source_from_other_users_list(self):
        list = get_object_or_404(List, name="TestList2")
        list.sources.add(get_object_or_404(Source, name="TestSource1"))
        list.sources.add(get_object_or_404(Source, name="TestSource2"))
        source = get_object_or_404(Source, name="TestSource1")
        self.assertTrue(list.sources.filter(source_id=source.source_id).exists())
        self.client.delete(f"/api/lists/{list.list_id}/delete_source_from_list/{source.source_id}/")
        self.assertTrue(list.sources.filter(source_id=source.source_id).exists())

    def test_delete_article_from_list(self):
        list = get_object_or_404(List, name="TestList1")
        article = get_object_or_404(Article, title="TestArticle1")
        list.articles.add(article)
        list.articles.add(get_object_or_404(Article, title="TestArticle2"))
        self.assertTrue(list.articles.filter(article_id=article.article_id).exists())
        self.client.delete(f"/api/lists/{list.list_id}/delete_article_from_list/{article.article_id}/")
        self.assertFalse(list.articles.filter(article_id=article.article_id).exists())

    def test_try_to_delete_article_from_other_users_list(self):
        list = get_object_or_404(List, name="TestList2")
        article = get_object_or_404(Article, title="TestArticle1")
        list.articles.add(article)
        list.articles.add(get_object_or_404(Article, title="TestArticle2"))
        self.assertTrue(list.articles.filter(article_id=article.article_id).exists())
        self.client.delete(f"/api/lists/{list.list_id}/delete_article_from_list/{article.article_id}/")
        self.assertTrue(list.articles.filter(article_id=article.article_id).exists())

    def test_add_source_to_list(self):
        list = get_object_or_404(List, name="TestList1")
        source = get_object_or_404(Source, name="TestSource1")
        self.assertFalse(list.sources.filter(source_id=source.source_id).exists())
        self.client.post(f"/api/lists/{list.list_id}/add_source/{source.source_id}/")
        self.assertTrue(list.sources.filter(source_id=source.source_id).exists())

    def test_try_to_add_source_to_other_users_list(self):
        list = get_object_or_404(List, name="TestList2")
        source = get_object_or_404(Source, name="TestSource1")
        self.assertFalse(list.sources.filter(source_id=source.source_id).exists())
        self.client.post(f"/api/lists/{list.list_id}/add_source/{source.source_id}/")
        self.assertFalse(list.sources.filter(source_id=source.source_id).exists())

    def test_add_article_to_list(self):
        list = get_object_or_404(List, name="TestList1")
        article = get_object_or_404(Article, title="TestArticle1")
        self.assertFalse(list.articles.filter(article_id=article.article_id).exists())
        self.client.post(f"/api/lists/{list.list_id}/add_article_to_list/{article.article_id}/")
        self.assertTrue(list.articles.filter(article_id=article.article_id).exists())

    def test_try_to_add_article_to_other_users_list(self):
        list = get_object_or_404(List, name="TestList2")
        article = get_object_or_404(Article, title="TestArticle1")
        self.assertFalse(list.articles.filter(article_id=article.article_id).exists())
        self.client.post(f"/api/lists/{list.list_id}/add_article_to_list/{article.article_id}/")
        self.assertFalse(list.articles.filter(article_id=article.article_id).exists())


class NotificationViewSetTest(APITestCase):

    def setUp(self):
        create_test_users()
        self.client.login(username="TestUser1", password="testpw99")
        create_test_lists()
        create_test_notifications()
        create_test_website()
        create_test_sectors()
        create_test_sources()

    def test_list_notification_creation(self):
        list = get_object_or_404(List, name="TestList8")
        data = {'list_id': list.list_id}
        self.assertFalse(Notification.objects.filter(list=list, user=get_object_or_404(User, username="TestUser1")).exists())
        self.client.post(f"/api/notifications/", data)
        self.assertTrue(Notification.objects.filter(list=list, user=get_object_or_404(User, username="TestUser1")).exists())

    def test_source_notification_creation(self):
        source = get_object_or_404(Source, name="TestSource8")
        data = {'source_id': source.source_id}
        self.assertFalse(Notification.objects.filter(source=source, user=get_object_or_404(User, username="TestUser1")).exists())
        self.client.post(f"/api/notifications/", data)
        self.assertTrue(Notification.objects.filter(source=source, user=get_object_or_404(User, username="TestUser1")).exists())


class FilteredListsTest(APITestCase):

    def setUp(self):
        create_test_users()
        create_test_lists()

    def test_filtered_lists_view(self):
        list = get_object_or_404(List, name="TestList1")
        list.is_public = False
        list.save()
        response = self.client.get(f"/api/search_lists/TestList")
        self.assertEqual(len(response.json()), 9)


class FilteredArticlesTest(APITestCase):

    def setUp(self):
        create_test_users()
        create_test_website()
        create_test_sectors()
        create_test_sources()
        create_test_articles()

    def test_filtered_articles_view(self):
        response = self.client.get(f"/api/search_articles/TestArticle")
        self.assertEqual(len(response.json()[0]), 10)


class FilteredSiteTest(APITestCase):

    def setUp(self):
        create_test_users()
        create_test_website()
        create_test_sectors()
        create_test_sources()
        create_test_articles()
        create_test_lists()

    def test_filtered_site_view(self):
        response = self.client.get(f"/api/search_site/Test")
        self.assertEqual(len(response.json()[0]), 3)
        self.assertEqual(len(response.json()[1]), 3)
        self.assertEqual(len(response.json()[2]), 3)