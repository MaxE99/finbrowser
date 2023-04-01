# Django imports
from django.test import TestCase
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model


# Local imports
from apps.tests.test_instances import CreateTestInstances
from apps.source.models import Source, SourceRating
from apps.sector.models import Sector


User = get_user_model()


class TestSourceManager(CreateTestInstances, TestCase):
    # def test_get_similiar_sources(self): # makes no sense to test this
    #     pass

    def test_filter_subscribed_sources_by_content_type(self):
        user = get_object_or_404(User, username="TestUser1")
        Source.objects.filter_subscribed_sources_by_content_type(user)

    def test_filter_by_sector(self):
        sector = get_object_or_404(Sector, name="TestSector1")
        sources_by_sector = Source.objects.filter_by_sector(sector)
        self.assertEqual(sources_by_sector["analysis_sources"].count(), 1)
        self.assertEqual(sources_by_sector["commentary_sources"].count(), 1)
        self.assertEqual(sources_by_sector["news_sources"].count(), 1)

    def test_filter_by_subscription(self):
        user = get_object_or_404(User, username="TestUser1")
        subscribed_sources = Source.objects.filter_by_subscription(user)
        self.assertEqual(subscribed_sources.count(), 3)

    def test_filter_by_search_term(self):
        filtered_sources = Source.objects.filter_by_search_term("F")
        self.assertEqual(filtered_sources.count(), 1)

    # def test_filter_by_list_and_search_term_exclusive(self):
    #     pass

    # def test_filter_by_subscription_and_search_term_exclusive(self):
    #     pass

    def test_get_random_top_sources(self):
        random_top_sources = Source.objects.get_random_top_sources()
        self.assertEqual(random_top_sources.count(), 5)


class TestSourceRatingManager(CreateTestInstances, TestCase):
    def test_get_user_rating(self):
        user = get_object_or_404(User, username="TestUser1")
        source = get_object_or_404(Source, name="TestSource1")
        source_rating = SourceRating.objects.get_user_rating(user, source)
        self.assertEqual(source_rating, 5)

    def test_get_average_rating(self):
        source = get_object_or_404(Source, name="TestSource1")
        average_rating = SourceRating.objects.get_average_rating(source)
        self.assertEqual(average_rating, 2.8)

    def test_get_ammount_of_ratings(self):
        source = get_object_or_404(Source, name="TestSource1")
        average_rating = SourceRating.objects.get_ammount_of_ratings(source)
        self.assertEqual(average_rating, 4)

    def test_save_rating_new(self):
        user = get_object_or_404(User, username="TestUser1")
        source = get_object_or_404(Source, name="TestSource8")
        SourceRating.objects.save_rating(user, source, 2)
        source8_avg_rating = SourceRating.objects.get_average_rating(source)
        self.assertEqual(source8_avg_rating, 2)

    def test_save_rating_update(self):
        user = get_object_or_404(User, username="TestUser1")
        source = get_object_or_404(Source, name="TestSource1")
        SourceRating.objects.save_rating(user, source, 2)
        source_rating = SourceRating.objects.get_user_rating(user, source)
        self.assertEqual(source_rating, 2)
