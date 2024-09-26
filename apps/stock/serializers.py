# Django imports
from rest_framework import serializers
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone

# Local imports
from data.english_words import english_words
from apps.stock.models import Stock, PortfolioKeyword, PortfolioStock, Portfolio


class PortfolioSerializer(serializers.ModelSerializer):
    stocks = serializers.SerializerMethodField()

    def get_stocks(self, obj):
        return PortfolioStock.objects.filter(portfolio=obj).values_list(
            "stock", flat=True
        )

    class Meta:
        model = Portfolio
        fields = "__all__"


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__"


class PortfolioKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioKeyword
        fields = "__all__"


class PortfolioStockSerializer(serializers.ModelSerializer):
    filtered_content = serializers.SerializerMethodField()
    stock = StockSerializer()
    keywords = PortfolioKeywordSerializer(many=True)
    absolute_path = serializers.SerializerMethodField()
    articles = serializers.SerializerMethodField()
    last_article = serializers.SerializerMethodField()
    articles_last_7d = serializers.SerializerMethodField()

    def get_filtered_content(self, obj):
        self.filtered_content = self.context.get("filtered_content", None)
        return self.filtered_content

    def get_absolute_path(self, obj):
        return obj.stock.get_absolute_url

    def get_articles(self, obj):
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

    def get_last_article(self, obj):
        last_article = self.articles[0] if self.articles else None
        if last_article:
            return last_article.pub_date
        return None

    def get_articles_last_7d(self, obj):
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
