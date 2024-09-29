from typing import Any, List, Optional
from datetime import timedelta

from rest_framework import serializers
from django.db.models import Q
from django.utils import timezone

from data.english_words import english_words
from apps.stock.models import Stock, PortfolioKeyword, PortfolioStock, Portfolio


class PortfolioSerializer(serializers.ModelSerializer):
    """
    Serializer for the Portfolio model.
    """

    stocks = serializers.SerializerMethodField()

    def get_stocks(self, obj: Portfolio) -> List[int]:
        """
        Returns a list of stock IDs associated with the portfolio.

        Args:
            obj (Portfolio): The portfolio instance.

        Returns:
            List[int]: A list of stock IDs.
        """
        return PortfolioStock.objects.filter(portfolio=obj).values_list(
            "stock", flat=True
        )

    class Meta:
        model = Portfolio
        fields = "__all__"


class StockSerializer(serializers.ModelSerializer):
    """
    Serializer for the Stock model.
    """

    class Meta:
        model = Stock
        fields = "__all__"


class PortfolioKeywordSerializer(serializers.ModelSerializer):
    """
    Serializer for the PortfolioKeyword model.
    """

    class Meta:
        model = PortfolioKeyword
        fields = "__all__"


class PortfolioStockSerializer(serializers.ModelSerializer):
    """
    Serializer for the PortfolioStock model.
    """

    filtered_content = serializers.SerializerMethodField()
    stock = StockSerializer()
    keywords = PortfolioKeywordSerializer(many=True)
    absolute_path = serializers.SerializerMethodField()
    articles = serializers.SerializerMethodField()
    last_article = serializers.SerializerMethodField()
    articles_last_7d = serializers.SerializerMethodField()

    def get_filtered_content(self, obj: PortfolioStock) -> Optional[Any]:
        """
        Returns the filtered content from the context.

        Args:
            obj (PortfolioStock): The portfolio stock instance.

        Returns:
            Optional[Any]: The filtered content, if present.
        """
        self.filtered_content = self.context.get("filtered_content", None)
        return self.filtered_content

    def get_absolute_path(self, obj: PortfolioStock) -> str:
        """
        Returns the absolute URL of the associated stock.

        Args:
            obj (PortfolioStock): The portfolio stock instance.

        Returns:
            str: The absolute URL of the stock.
        """
        return obj.stock.get_absolute_url

    def get_articles(self, obj: PortfolioStock) -> List[Any]:
        """
        Returns a list of articles related to the stock and keywords.

        Args:
            obj (PortfolioStock): The portfolio stock instance.

        Returns:
            List[Any]: A list of articles related to the stock and keywords.
        """
        q_objects = Q()
        if len(obj.stock.ticker) > 1 and obj.stock.ticker.lower() not in english_words:
            q_objects.add(Q(search_vector=obj.stock.ticker), Q.OR)
        else:
            # important to use $ + instead of as f-string because $ has special meaning in f-string
            q_objects.add(Q(search_vector="$" + obj.stock.ticker), Q.OR)

        q_objects.add(Q(search_vector=obj.stock.short_company_name), Q.OR)
        for keyword in obj.keywords.all():
            q_objects.add(Q(search_vector=keyword.keyword), Q.OR)

        self.articles = list(self.filtered_content.filter(q_objects))
        return self.articles

    def get_last_article(self, obj: PortfolioStock):
        """
        Returns the publication date of the last article, if available.

        Args:
            obj (PortfolioStock): The portfolio stock instance.

        Returns:
            Optional[timezone]: The publication date of the last article or None if no articles exist.
        """
        last_article = self.articles[0] if self.articles else None
        if last_article:
            return last_article.pub_date
        return None

    def get_articles_last_7d(self, obj: PortfolioStock) -> int:
        """
        Returns the count of articles published in the last 7 days.

        Args:
            obj (PortfolioStock): The portfolio stock instance.

        Returns:
            int: The count of articles published in the last 7 days.
        """
        date_from = timezone.now() - timedelta(days=7)
        articles = self.articles

        if articles:
            filtered_articles = [
                article for article in articles if article.pub_date >= date_from
            ]
            count = len(filtered_articles)
            return count

        return 0

    class Meta:
        model = PortfolioStock
        fields = "__all__"
