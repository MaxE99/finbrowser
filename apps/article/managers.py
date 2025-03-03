from typing import Dict, List

from django.db import models
from django.db.models import Q

from data.english_words import english_words


class ArticleManager(models.Manager):
    """
    Custom manager for the Article model providing various methods
    to retrieve articles based on content type, subscriptions,
    portfolio stocks, and more.
    """

    def _get_content_by_type(
        self, source_ids: List[int], content_type: str
    ) -> models.QuerySet:
        """
        Helper method to filter content by type.

        Args:
            source_ids (List[int]): The list of source IDs to filter by.
            content_type (str): The content type to filter.

        Returns:
            QuerySet: Filtered articles of the specified content type.
        """
        return self.filter(
            source__in=source_ids, source__content_type=content_type
        ).select_related("source", "source__website", "tweet_type")

    def _get_content_by_subscribed_sources(
        self, subscribed_sources: List[int]
    ) -> models.QuerySet:
        """
        Helper method to filter content by subscribed sources.

        Args:
            subscribed_sources (list): The subscribed source IDs to filter.

        Returns:
            QuerySet: Filtered articles from the subscribed sources.
        """
        return self.filter(source__in=subscribed_sources).select_related(
            "source", "source__website", "tweet_type"
        )

    def get_list_content_by_content_type(
        self, list_sources: models.QuerySet
    ) -> Dict[str, models.QuerySet]:
        """
        Retrieve articles grouped by content type from the given list of sources.

        Args:
            list_sources (QuerySet): The sources to filter articles.

        Returns:
            Dict[str, models.QuerySet]: Three QuerySets containing articles filtered by
                   Analysis, Commentary, and News content types.
        """
        source_ids = list_sources.values_list("source_id", flat=True)

        analysis = self._get_content_by_type(source_ids, "Analysis")
        commentary = self._get_content_by_type(source_ids, "Commentary")
        news = self._get_content_by_type(source_ids, "News")

        return {"analysis": analysis, "commentary": commentary, "news": news}

    def get_subscribed_content_by_content_type(
        self, subscribed_sources: Dict[str, List[int]]
    ) -> Dict[str, models.QuerySet]:
        """
        Retrieve articles based on subscribed content types.

        Args:
            subscribed_sources (Dict[str, List[int]]): A dictionary with lists of
                                       subscribed source IDs by content type.

        Returns:
            Dict[str, models.QuerySet]: Three QuerySets containing articles filtered by
                   Analysis, Commentary, and News content types.
        """
        analysis_content = self._get_content_by_subscribed_sources(
            subscribed_sources["analysis"]
        )
        commentary_content = self._get_content_by_subscribed_sources(
            subscribed_sources["commentary"]
        )
        news_content = self._get_content_by_subscribed_sources(
            subscribed_sources["news"]
        )

        return {
            "analysis": analysis_content,
            "commentary": commentary_content,
            "news": news_content,
        }

    def get_portfolio_content(self, portfolio_stocks: List) -> models.QuerySet:
        """
        Retrieve articles associated with the given portfolio stocks.

        Args:
            portfolio_stocks (list): A list of portfolio stock dictionaries.

        Returns:
            QuerySet: Filtered articles associated with the specified stocks.
        """
        article_ids = [
            article_id
            for stock in portfolio_stocks
            for article_id in stock.get("articles").values_list("article_id", flat=True)
        ]
        return self.filter(article_id__in=article_ids).select_related(
            "source", "source__website", "tweet_type"
        )

    def get_content_about_stock(self, stock) -> models.QuerySet:
        """
        Retrieve articles related to a specific stock.

        Args:
            stock (Stock): The stock object to retrieve content for.

        Returns:
            QuerySet: Filtered articles related to the stock.
        """
        q_objects = Q()

        if len(stock.ticker) == 2 and stock.ticker.lower() not in english_words:
            q_objects.add(Q(search_vector=f"${stock.ticker} "), Q.OR)
        elif len(stock.ticker) > 2 and stock.ticker.lower() not in english_words:
            q_objects.add(Q(search_vector=stock.ticker), Q.OR)

        if stock.short_company_name.lower() not in english_words:
            q_objects.add(Q(search_vector=stock.short_company_name), Q.OR)

        return (
            self.filter(q_objects).select_related(
                "source", "tweet_type", "source__website"
            )
            if q_objects
            else self.none()
        )

    def filter_by_search_term(self, search_term: str) -> models.QuerySet:
        """
        Filter articles based on a search term.

        Args:
            search_term (str): The search term to filter articles by.

        Returns:
            QuerySet: Filtered articles or an empty QuerySet if no term is provided.
        """
        return (
            self.filter(search_vector=search_term).select_related(
                "source", "tweet_type", "source__website"
            )
            if len(search_term) > 1
            else self.none()
        )

    def filter_by_source(self, source) -> models.QuerySet:
        """
        Filter articles by a specific source.

        Args:
            source (Source): The source to filter articles by.

        Returns:
            QuerySet: Filtered articles associated with the specified source.
        """
        return self.filter(source=source).select_related(
            "source", "source__website", "tweet_type"
        )

    def get_latest_analysis(self) -> models.QuerySet:
        """
        Retrieve the latest analysis articles.

        Returns:
            QuerySet: Latest analysis articles.
        """
        return self.filter(source__content_type="Analysis").select_related("source")[
            0:5
        ]

    def get_latest_news(self) -> models.QuerySet:
        """
        Retrieve the latest news articles.

        Returns:
            QuerySet: Latest news articles.
        """
        return self.filter(source__content_type="News").select_related("source")[0:5]

    def get_top_content_anon(self) -> models.QuerySet:
        """
        Retrieve top content articles

        Returns:
            QuerySet: Filtered top articles.
        """
        return self.filter(source__top_source=True).select_related(
            "source", "source__website"
        )

    def get_stock_pitches(self) -> models.QuerySet:
        """
        Retrieve articles related to stock pitches.

        Returns:
            QuerySet: Filtered articles associated with stock pitches.
        """

        from apps.article.models import StockPitch

        stock_pitches = StockPitch.objects.all().values_list("article")
        return self.filter(article_id__in=stock_pitches).select_related(
            "source", "source__website"
        )


class HighlightedArticlesManager(models.Manager):
    """
    Custom manager for the HighlightedArticles model to provide
    methods for retrieving highlighted articles based on user.
    """

    def get_ids_by_user(self, user):
        """
        Retrieve a list of article IDs highlighted by a specific user.

        Args:
            user (User): The user object for whom to retrieve highlighted articles.

        Returns:
            QuerySet: A flat list of article IDs highlighted by the specified user.
        """
        return self.filter(user=user).values_list("article", flat=True)
