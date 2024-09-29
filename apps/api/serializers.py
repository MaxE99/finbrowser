from typing import Any, Dict

from django.shortcuts import get_object_or_404
from django.utils.timezone import localtime
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from apps.accounts.models import Profile, Website
from apps.source.models import Source, SourceRating, SourceTag
from apps.article.models import Article, HighlightedArticle, TweetType
from apps.list.models import List
from apps.home.models import Notification
from apps.stock.models import Stock, Portfolio, PortfolioStock, PortfolioKeyword


class ListSerializer(serializers.ModelSerializer):
    """
    Serializer for the List model.

    This serializer handles the serialization and deserialization of List objects,
    including handling related articles and sources, as well as setting the creator field
    during create and update operations.
    """

    name = serializers.CharField(default="New List", required=False)
    article_id = serializers.IntegerField(required=False)
    source_id = serializers.IntegerField(required=False)

    def __init__(self, *args: Any, **kwargs: Any):
        """
        Initializes the ListSerializer.

        If the request method is PATCH or POST, sets the creator field in the request data
        to the primary key of the authenticated user.

        Args:
            args (Any): Positional arguments.
            kwargs (Any): Keyword arguments.
        """
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

    def update(self, instance: List, validated_data: Dict[str, Any]) -> List:
        """
        Updates the instance of the List model with validated data.

        This method handles the addition or removal of articles and sources based on
        the provided article_id and source_id. It also updates the list name and
        manages the 'main' status of the list.

        Args:
            instance (List): The instance of the List model to update.
            validated_data (Dict[str, Any]): The validated data for the update.

        Returns:
            List: The updated instance of the List model.

        Raises:
            NotFound: If the article or source is not found.
        """
        article_id = validated_data.get("article_id")
        source_id = validated_data.get("source_id")
        name = validated_data.get("name")

        if article_id:
            article = get_object_or_404(Article, article_id=article_id)
            if article in instance.articles.all():
                instance.articles.remove(article)
            else:
                instance.articles.add(article)

        elif source_id:
            source = get_object_or_404(Source, source_id=source_id)
            if source in instance.sources.all():
                instance.sources.remove(source)
            else:
                instance.sources.add(source)

        elif name:
            instance.name = name
            if validated_data.get("main"):
                main_list = get_object_or_404(
                    List, creator=validated_data.get("creator"), main=True
                )
                main_list.main = False
                main_list.save()
                instance.main = True

        return super().update(instance, validated_data)


class WebsiteSerializer(serializers.ModelSerializer):
    """
    Serializer for the Website model.

    This serializer handles the serialization and deserialization of Website objects.
    """

    class Meta:
        model = Website
        fields = "__all__"


class SourceSerializer(serializers.ModelSerializer):
    """
    Serializer for the Source model.

    This serializer handles the serialization and deserialization of Source objects,
    including managing subscribers.
    """

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

    def update(self, instance: Source, validated_data: Dict[str, Any]) -> Source:
        """
        Updates the instance of the Source model by toggling the user's subscription.

        If the user is already a subscriber, they will be removed. Otherwise, they will be added.

        Args:
            instance (Source): The instance of the Source model to update.
            validated_data (Dict[str, Any]): The validated data for the update.

        Returns:
            Source: The updated instance of the Source model.
        """
        user = self.context["request"].user
        if user in instance.subscribers.all():
            instance.subscribers.remove(user)
        else:
            instance.subscribers.add(user)

        return super().update(instance, validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model.

    This serializer handles the serialization and deserialization of Profile objects.
    """

    class Meta:
        model = Profile
        fields = "__all__"

    def update(self, instance: Profile, validated_data: Dict[str, Any]) -> Profile:
        """
        Updates the instance of the Profile model.

        If a profile picture is provided, it updates it; otherwise, it deletes the existing profile picture.

        Args:
            instance (Profile): The instance of the Profile model to update.
            validated_data (Dict[str, Any]): The validated data for the update.

        Returns:
            Profile: The updated instance of the Profile model.
        """
        if validated_data.get("profile_pic"):
            instance.profile_pic = validated_data.get("profile_pic")
        else:
            instance.profile_pic.delete()

        return super().update(instance, validated_data)


class SourceRatingSerializer(serializers.ModelSerializer):
    """
    Serializer for the SourceRating model.

    This serializer handles the serialization and deserialization of SourceRating objects,
    including the creation and update of user ratings for sources.
    """

    class Meta:
        model = SourceRating
        fields = "__all__"

    def __init__(self, *args: Any, **kwargs: Any):
        """
        Initializes the SourceRatingSerializer.

        Sets the user field in the request data to the primary key of the authenticated user.

        Args:
            args (Any): Positional arguments.
            kwargs (Any): Keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.context["request"].data["user"] = self.context["request"].user.pk

    def create(self, validated_data: Dict[str, Any]) -> SourceRating:
        """
        Creates a new SourceRating or updates an existing one if a rating already exists for the user.

        Args:
            validated_data (Dict[str, Any]): The validated data for the creation.

        Returns:
            SourceRating: The created or updated SourceRating instance.
        """
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
    """
    Serializer for the HighlightedArticle model.

    This serializer handles the serialization and deserialization of HighlightedArticle objects,
    including associating the user with the highlighted article.
    """

    class Meta:
        model = HighlightedArticle
        fields = "__all__"

    def __init__(self, *args: Any, **kwargs: Any):
        """
        Initializes the HighlightedArticleSerializer.

        Sets the user field in the request data to the primary key of the authenticated user.

        Args:
            args (Any): Positional arguments.
            kwargs (Any): Keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.context["request"].data["user"] = self.context["request"].user.pk


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.

    This serializer handles the serialization and deserialization of Notification objects,
    including checks for keyword uniqueness for the user.
    """

    class Meta:
        model = Notification
        fields = "__all__"

    def __init__(self, *args: Any, **kwargs: Any):
        """
        Initializes the NotificationSerializer.

        Sets the user field in the request data to the primary key of the authenticated user.

        Args:
            args (Any): Positional arguments.
            kwargs (Any): Keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.context["request"].data["user"] = self.context["request"].user.pk

    def create(self, validated_data: Dict[str, Any]) -> Notification:
        """
        Creates a new Notification instance after checking for keyword uniqueness.

        If the keyword already exists for the user, a PermissionDenied exception is raised.

        Args:
            validated_data (Dict[str, Any]): The validated data for the creation.

        Returns:
            Notification: The created Notification instance.

        Raises:
            PermissionDenied: If the keyword is already associated with the user.
        """
        if validated_data.get("keyword"):
            user_keywords = Notification.objects.filter(
                user=validated_data.get("user"), keyword__isnull=False
            ).values_list("keyword", flat=True)

            if validated_data.get("keyword") in user_keywords:
                raise PermissionDenied(
                    "You have already created a keyword with that name!"
                )

        return super().create(validated_data)


class SourceTagSerializer(serializers.ModelSerializer):
    """
    Serializer for the SourceTag model.

    This serializer handles the serialization and deserialization of SourceTag objects.
    """

    class Meta:
        model = SourceTag
        fields = "__all__"


class PortfolioSerializer(serializers.ModelSerializer):
    """
    Serializer for the Portfolio model.

    This serializer handles the serialization and deserialization of Portfolio objects,
    including management of blacklisted sources and main portfolio status.
    """

    name = serializers.CharField(default="New Portfolio")
    source_id = serializers.IntegerField(required=False)

    def __init__(self, *args: Any, **kwargs: Any):
        """
        Initializes the PortfolioSerializer.

        Sets the user field in the request data to the primary key of the authenticated user
        if the request method is PATCH or POST.

        Args:
            args (Any): Positional arguments.
            kwargs (Any): Keyword arguments.
        """
        super().__init__(*args, **kwargs)
        if self.context.get("request") and self.context["request"].method in [
            "PATCH",
            "POST",
        ]:
            self.context["request"].data["user"] = self.context["request"].user.pk

    class Meta:
        model = Portfolio
        fields = "__all__"

    def update(self, instance: Portfolio, validated_data: Dict[str, Any]) -> Portfolio:
        """
        Updates the instance of the Portfolio model.

        Manages blacklisted sources and updates the portfolio's main status.

        Args:
            instance (Portfolio): The instance of the Portfolio model to update.
            validated_data (Dict[str, Any]): The validated data for the update.

        Returns:
            Portfolio: The updated instance of the Portfolio model.
        """
        source_id = validated_data.get("source_id")

        if source_id:
            source = get_object_or_404(Source, source_id=source_id)
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
    """
    Serializer for the Stock model.

    This serializer handles the serialization and deserialization of Stock objects.
    """

    class Meta:
        model = Stock
        fields = "__all__"


class PortfolioKeywordSerializer(serializers.ModelSerializer):
    """
    Serializer for the PortfolioKeyword model.

    This serializer handles the serialization and deserialization of PortfolioKeyword objects,
    ensuring that keywords are unique per portfolio.
    """

    pstock_id = serializers.IntegerField(write_only=True)
    user = serializers.IntegerField(write_only=True)

    def __init__(self, *args: Any, **kwargs: Any):
        """
        Initializes the PortfolioKeywordSerializer.

        Sets the user field in the request data to the primary key of the authenticated user.

        Args:
            args (Any): Positional arguments.
            kwargs (Any): Keyword arguments.
        """
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None:
            request.data["user"] = request.user.pk

    class Meta:
        model = PortfolioKeyword
        fields = "__all__"

    def create(self, validated_data: Dict[str, Any]) -> PortfolioKeyword:
        """
        Creates a new PortfolioKeyword instance, ensuring unique keywords per portfolio.

        Args:
            validated_data (Dict[str, Any]): The validated data for the creation.

        Returns:
            PortfolioKeyword: The created PortfolioKeyword instance.

        Raises:
            PermissionDenied: If the keyword already exists for the portfolio or the maximum limit is exceeded.
        """
        pstock = get_object_or_404(
            PortfolioStock,
            pstock_id=validated_data.get("pstock_id"),
            portfolio__user=validated_data.get("user"),  # validation
        )
        portfolio_keywords = PortfolioKeyword.objects.filter(
            portfolio_stocks__portfolio=pstock.portfolio
        ).values_list("keyword", flat=True)
        given_keyword = validated_data.get("keyword")

        if given_keyword in portfolio_keywords:
            raise PermissionDenied(
                "This portfolio already has a keyword with that name!"
            )
        if portfolio_keywords.count() > 99:
            raise PermissionDenied(
                "You have already created the maximum number of objects allowed."
            )

        keyword = PortfolioKeyword.objects.create(keyword=given_keyword)
        pstock.keywords.add(keyword)
        return keyword


class PortfolioStockSerializer(serializers.ModelSerializer):
    """
    Serializer for the PortfolioStock model.

    This serializer handles the serialization and deserialization of PortfolioStock objects,
    including associated keywords.
    """

    stocks = serializers.ListField(write_only=True, child=serializers.IntegerField())
    keywords = PortfolioKeywordSerializer(read_only=True, many=True)

    class Meta:
        model = PortfolioStock
        fields = "__all__"
        extra_kwargs = {"stock": {"read_only": True}}


class TweetTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for the TweetType model.

    This serializer handles the serialization and deserialization of TweetType objects.
    """

    class Meta:
        model = TweetType
        fields = "__all__"


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Article model.

    This serializer handles the serialization and deserialization of Article objects,
    including derived fields like publication date and highlight status.
    """

    source = SourceSerializer(read_only=True)
    pub_date = serializers.SerializerMethodField()
    is_highlighted = serializers.SerializerMethodField()
    tweet_type = TweetTypeSerializer(read_only=True, required=False)

    def get_pub_date(self, obj: Article) -> str:
        """
        Formats the publication date for display.

        Args:
            obj (Article): The Article instance.

        Returns:
            str: The formatted publication date.
        """
        return (
            localtime(obj.pub_date)
            .strftime("%b. %d, %Y, %-I:%M %p")
            .replace("AM", "a.m.")
            .replace("PM", "p.m.")
            .replace(":00", "")
        )

    def get_is_highlighted(self, obj: Article) -> bool:
        """
        Checks if the article is highlighted for the authenticated user.

        Args:
            obj (Article): The Article instance.

        Returns:
            bool: True if highlighted, False otherwise.
        """
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return HighlightedArticle.objects.filter(
                user=request.user, article=obj
            ).exists()
        return False

    class Meta:
        model = Article
        fields = "__all__"
