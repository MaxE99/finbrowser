# Django imports
from django.db import models
from django.db.models import Q

# Local imports
from apps.scrapper.english_words import english_words


class ArticleManager(models.Manager):
    def get_list_content_by_content_type(self, list_sources):
        source_ids = list_sources.values_list("source_id", flat=True)
        analysis = self.filter(
            source__in=source_ids,
            source__content_type="Analysis",
        ).select_related("source", "source__website", "tweet_type")
        commentary = self.filter(
            source__in=source_ids,
            source__content_type="Commentary",
        ).select_related("source", "source__website", "tweet_type")
        news = self.filter(
            source__in=source_ids,
            source__content_type="News",
        ).select_related("source", "source__website", "tweet_type")
        return analysis, commentary, news

    def get_subscribed_content_by_content_type(self, subscribed_sources):
        analysis_content = self.filter(
            source__in=subscribed_sources["analysis"]
        ).select_related("source", "source__website", "tweet_type")
        commentary_content = self.filter(
            source__in=subscribed_sources["commentary"]
        ).select_related("source", "source__website", "tweet_type")
        news_content = self.filter(
            source__in=subscribed_sources["news"]
        ).select_related("source", "source__website", "tweet_type")
        return analysis_content, commentary_content, news_content

    def get_portfolio_content(self, portfolio_stocks):
        article_ids = []
        for stock in portfolio_stocks:
            article_ids += list(
                stock.get("articles").values_list("article_id", flat=True)
            )
        return self.filter(article_id__in=article_ids).select_related(
            "source", "source__website", "tweet_type"
        )

    def get_content_about_stock(self, stock):
        if len(stock.ticker) > 1 and stock.ticker.lower() not in english_words:
            return self.filter(
                Q(search_vector=stock.ticker)
                | Q(search_vector=stock.short_company_name)
            ).select_related("source", "tweet_type", "source__website")
        return self.filter(
            Q(title__contains=f"${stock.ticker} ")
            | Q(search_vector=stock.short_company_name)
        ).select_related("source", "tweet_type", "source__website")

    def filter_by_search_term(self, search_term):
        if len(search_term) > 1:
            return self.filter(search_vector=search_term).select_related(
                "source", "tweet_type", "source__website"
            )
        return self.none()

    def filter_by_source(self, source):
        return self.filter(source=source).select_related(
            "source", "source__website", "tweet_type"
        )

    def get_best_tweets_anon(self):
        return self.filter(
            source__top_source=True, source__website__name="Twitter"
        ).select_related("source", "source__website", "tweet_type")

    def get_latest_analysis(self):
        return self.filter(source__content_type="Analysis").select_related("source")[
            0:5
        ]

    def get_latest_news(self):
        return self.filter(source__content_type="News").select_related("source")[0:5]

    def get_top_content_anon(self):
        return (
            self.filter(source__top_source=True)
            .exclude(source__website__name="Twitter")
            .select_related("source", "source__website")
        )


class HighlightedArticlesManager(models.Manager):
    def get_ids_by_user(self, user):
        return self.filter(user=user).values_list("article", flat=True)
