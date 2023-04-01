# Django imports
from django.test import TestCase
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

# Local imports
from apps.tests.test_instances import CreateTestInstances
from apps.article.models import Article
from apps.list.models import List
from apps.source.models import Source
from apps.stock.models import Stock

User = get_user_model()


class TestArticleManager(CreateTestInstances, TestCase):
    def test_get_list_content_by_content_type(self):
        selected_list = get_object_or_404(List, name="List1")
        analysis, commentary, news = Article.objects.get_list_content_by_content_type(
            selected_list.sources.all()
        )
        self.assertEqual(analysis.count(), 7)
        self.assertEqual(commentary.count(), 2)
        self.assertEqual(news.count(), 0)

    def test_get_subscribed_content_by_content_type(self):
        user = get_object_or_404(User, username="TestUser1")
        subscribed_sources = Source.objects.filter_subscribed_sources_by_content_type(
            user
        )
        (
            analysis_content,
            commentary_content,
            news_content,
        ) = Article.objects.get_subscribed_content_by_content_type(subscribed_sources)
        self.assertEqual(analysis_content.count(), 7)
        self.assertEqual(commentary_content.count(), 2)
        self.assertEqual(news_content.count(), 3)

    # def test_get_portfolio_content(self): # makes no sense to test because of dependence
    #     pass

    def test_get_content_about_stock_single_letter_ticker(self):
        stock = get_object_or_404(Stock, ticker="F")
        stock_content = Article.objects.get_content_about_stock(stock)
        self.assertEqual(stock_content.count(), 2)

    def test_filter_by_search_term(self):
        search_results = Article.objects.filter_by_search_term("Ford")
        self.assertEqual(search_results.count(), 1)

    def test_filter_by_source(self):
        source = get_object_or_404(Source, name="TestSource1")
        source_articles = Article.objects.filter_by_source(source)
        self.assertEqual(source_articles.count(), 7)

    def test_get_best_tweets_anon(self):
        top_tweets = Article.objects.get_best_tweets_anon()
        self.assertEqual(top_tweets.count(), 1)

    def test_get_latest_analysis(self):
        latest_analysis = Article.objects.get_latest_analysis()
        self.assertEqual(latest_analysis.count(), 5)

    def test_get_latest_news(self):
        latest_news = Article.objects.get_latest_news()
        self.assertEqual(latest_news.count(), 3)

    def test_get_top_content_anon(self):
        top_content = Article.objects.get_top_content_anon()
        self.assertEqual(top_content.count(), 9)
