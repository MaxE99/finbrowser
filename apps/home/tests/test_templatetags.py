# Django imports
from django.test import TestCase
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

# Local imports
from apps.home.templatetags.tags import (
    calc_ranking,
    check_has_rated,
    get_article_ids_in_list,
    get_source_ids_in_list,
    get_time_since_last_content_published,
)
from apps.source.models import SourceRating, Source
from apps.list.models import List
from apps.tests.test_instances import CreateTestInstances
from apps.article.models import Article


User = get_user_model()


class TemplateTagsTestCase(CreateTestInstances, TestCase):
    def test_calc_ranking(self):
        counter = 0
        page_rank = 1
        result = calc_ranking(counter, page_rank)
        self.assertEqual(result, 0)

        counter = 25
        page_rank = 2
        result = calc_ranking(counter, page_rank)
        self.assertEqual(result, 50)

        counter = 50
        page_rank = 3
        result = calc_ranking(counter, page_rank)
        self.assertEqual(result, 100)

    def test_check_has_rated(self):
        user = get_object_or_404(User, username="TestUser1")
        user_ratings = SourceRating.objects.get_user_ratings_dict(user)
        source = get_object_or_404(Source, name="TestSource1")
        rating = check_has_rated(source, user_ratings)
        self.assertEqual(rating, 5)
        source = get_object_or_404(Source, name="TestSource9")
        rating = check_has_rated(source, user_ratings)
        self.assertFalse(rating)

    def test_check_get_source_ids_in_list(self):
        list = get_object_or_404(List, name="List1")
        source_ids = get_source_ids_in_list(list.sources.all())
        self.assertEqual(source_ids, [1, 3, 9])

    def test_check_get_article_ids_in_list(self):
        list = get_object_or_404(List, name="List1")
        article_ids = get_article_ids_in_list(list.articles.all())
        self.assertEqual(article_ids, [1])

    def test_get_time_since_last_content_published(self):
        article = get_object_or_404(Article, title="TestArticle1")
        time_since = get_time_since_last_content_published(article.pub_date)
        self.assertEqual(time_since, "2 days ago")
