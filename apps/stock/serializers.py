# Django imports
from rest_framework import serializers
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone

# Local imports
from apps.stock.models import Stock, PortfolioKeyword, PortfolioStock, Portfolio
from apps.article.models import Article


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
    articles = serializers.SerializerMethodField()
    last_article = serializers.SerializerMethodField()
    articles_last_7d = serializers.SerializerMethodField()
    stock = StockSerializer()
    keywords = PortfolioKeywordSerializer(many=True)
    absolute_path = serializers.SerializerMethodField()

    def get_articles(self, obj):
        q_objects = Q()
        if len(obj.stock.ticker) > 1:
            q_objects.add(Q(search_vector=obj.stock.ticker), Q.OR)
        else:
            q_objects.add(Q(title__contains=f"${obj.stock.ticker} "), Q.OR)
        q_objects.add(Q(search_vector=obj.stock.short_company_name), Q.OR)
        for keyword in obj.keywords.all():
            q_objects.add(Q(search_vector=keyword.keyword), Q.OR)
        self.articles = Article.objects.filter(q_objects).exclude(
            source__in=obj.portfolio.blacklisted_sources.all()
        )
        return self.articles

    def get_last_article(self, obj):
        last_article = self.articles.first()
        if last_article:
            return last_article.pub_date
        return None

    def get_articles_last_7d(self, obj):
        date_from = timezone.now() - timedelta(days=7)
        articles = self.articles
        if articles:
            return articles.filter(pub_date__gte=date_from).count()
        return 0

    def get_absolute_path(self, obj):
        return obj.stock.get_absolute_url

    class Meta:
        model = PortfolioStock
        fields = "__all__"
