# Django imports
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.utils.timezone import localtime

# Local imports
from apps.accounts.models import Profile, Website
from apps.source.models import Source, SourceRating, SourceTag
from apps.article.models import Article, HighlightedArticle, TweetType
from apps.list.models import List
from apps.home.models import Notification
from apps.stock.models import Stock, Portfolio, PortfolioStock, PortfolioKeyword


class ListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(default="New List", required=False)
    article_id = serializers.IntegerField(required=False)
    source_id = serializers.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get("request") and self.context["request"].method in [
            "PATCH",
            "POST",
        ]:
            self.context["request"].data["creator"] = self.context["request"].user.pk

    class Meta:
        model = List
        fields = "__all__"
        partial = ("main",)

    def update(self, instance, validated_data):
        if validated_data.get("article_id"):
            article = get_object_or_404(
                Article, article_id=validated_data.get("article_id")
            )
            if article in instance.articles.all():
                instance.articles.remove(article)
            else:
                instance.articles.add(article)
        elif validated_data.get("source_id"):
            source = get_object_or_404(
                Source, source_id=validated_data.get("source_id")
            )
            if source in instance.sources.all():
                instance.sources.remove(source)
            else:
                instance.sources.add(source)
        elif validated_data.get("name"):
            instance.name = validated_data.get("name")
            if validated_data.get("main"):
                main_list = get_object_or_404(
                    List, creator=validated_data.get("creator"), main=True
                )
                main_list.main = False
                main_list.save()
                instance.main = True
        return super().update(instance, validated_data)


class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = "__all__"


class SourceSerializer(serializers.ModelSerializer):
    website = WebsiteSerializer(read_only=True)

    class Meta:
        model = Source
        fields = "__all__"
        read_only_fields = [
            "source_id",
            "url",
            "slug",
            "name",
            "favicon_path",
            "paywall",
            "website",
            "sim_sources",
            "top_source",
            "sector",
            "external_id",
            "average_rating",
            "ammount_of_ratings",
            "content_type",
            "tags",
        ]

    def update(self, instance, validated_data):
        user = self.context["request"].user
        if user in instance.subscribers.all():
            instance.subscribers.remove(user)
        else:
            instance.subscribers.add(user)
        return super().update(instance, validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"

    def update(self, instance, validated_data):
        if validated_data.get("profile_pic"):
            instance.profile_pic = validated_data.get("profile_pic")
        else:
            instance.profile_pic.delete()
        return super().update(instance, validated_data)


class SourceRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceRating
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context["request"].data["user"] = self.context["request"].user.pk

    def create(self, validated_data):
        source_rating = SourceRating.objects.filter(
            user=validated_data.get("user"), source=validated_data.get("source")
        )
        if source_rating.exists():
            updated_rating = source_rating.first()
            updated_rating.rating = validated_data.get("rating")
            updated_rating.save()
            return updated_rating
        return super().create(validated_data)


class HighlightedArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HighlightedArticle
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context["request"].data["user"] = self.context["request"].user.pk


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context["request"].data["user"] = self.context["request"].user.pk


class SourceTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceTag
        fields = "__all__"


class PortfolioSerializer(serializers.ModelSerializer):
    name = serializers.CharField(default="New Portfolio")
    source_id = serializers.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get("request") and self.context["request"].method in [
            "PATCH",
            "POST",
        ]:
            self.context["request"].data["user"] = self.context["request"].user.pk

    class Meta:
        model = Portfolio
        fields = "__all__"

    def update(self, instance, validated_data):
        if validated_data.get("source_id"):
            source = get_object_or_404(
                Source, source_id=validated_data.get("source_id")
            )
            if source in instance.blacklisted_sources.all():
                instance.blacklisted_sources.remove(source)
            else:
                instance.blacklisted_sources.add(source)
        else:
            instance.name = validated_data.get("name")
            if validated_data.get("main"):
                main_portfolio = get_object_or_404(
                    Portfolio, user=validated_data.get("user"), main=True
                )
                main_portfolio.main = False
                main_portfolio.save()
                instance.main = True
        return super().update(instance, validated_data)


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__"


class PortfolioKeywordSerializer(serializers.ModelSerializer):
    pstock_id = serializers.IntegerField(write_only=True)
    user = serializers.IntegerField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "request" in self.context.keys():
            self.context["request"].data["user"] = self.context["request"].user.pk

    class Meta:
        model = PortfolioKeyword
        fields = "__all__"

    def create(self, validated_data):
        keyword = PortfolioKeyword.objects.create(keyword=validated_data.get("keyword"))
        pstock = get_object_or_404(
            PortfolioStock,
            pstock_id=validated_data.get("pstock_id"),
            portfolio__user=validated_data.get("user"),  # validation
        )
        pstock.keywords.add(keyword)
        return keyword


class PortfolioStockSerializer(serializers.ModelSerializer):
    stocks = serializers.ListField(write_only=True, child=serializers.IntegerField())
    keywords = PortfolioKeywordSerializer(read_only=True, many=True)

    class Meta:
        model = PortfolioStock
        fields = "__all__"
        extra_kwargs = {"stock": {"read_only": True}}


class TweetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TweetType
        fields = "__all__"


class ArticleSerializer(serializers.ModelSerializer):
    source = SourceSerializer(read_only=True)
    pub_date = serializers.SerializerMethodField()
    is_highlighted = serializers.SerializerMethodField()
    tweet_type = TweetTypeSerializer(read_only=True, required=False)

    def get_pub_date(self, obj):
        return (
            localtime(obj.pub_date)
            .strftime("%b. %d, %Y, %-I:%M %p")
            .replace("AM", "a.m.")
            .replace("PM", "p.m.")
            .replace(":00", "")
        )

    def get_is_highlighted(self, obj):
        request = self.context.get("request", None)
        if request and request.user.is_authenticated:
            return HighlightedArticle.objects.filter(
                user=request.user, article=obj
            ).exists()
        return False

    class Meta:
        model = Article
        fields = "__all__"
