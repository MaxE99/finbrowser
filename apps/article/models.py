# Django imports
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField

# Local imports
from apps.article.managers import ArticleManager, HighlightedArticlesManager
from apps.source.models import Source
from apps.stock.models import Stock

User = get_user_model()


class TweetType(models.Model):
    TYPE_CHOICES = [
        ("Image", "Image"),
        ("Link", "Link"),
        ("Retweet", "Retweet"),
        ("Basic", "Basic"),
        ("Quote", "Quote"),
        ("Reply", "Reply"),
    ]
    tweet_type_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="None")
    image_path = models.CharField(max_length=500, blank=True, null=True)
    text = models.CharField(max_length=500, blank=True, null=True)
    pub_date = models.DateTimeField(blank=True, null=True)
    author = models.CharField(max_length=100, blank=True, null=True)
    link = models.CharField(max_length=500, blank=True, null=True)
    initial_tweet_img_path = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.type} - {self.tweet_type_id}"


class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=500, db_index=True)
    link = models.URLField(max_length=500)
    pub_date = models.DateTimeField()
    source = models.ForeignKey(Source, blank=True, null=True, on_delete=models.CASCADE)
    external_id = models.CharField(unique=True, null=True, blank=True, max_length=100)
    tweet_type = models.ForeignKey(
        TweetType,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="tweet",
    )
    search_vector = SearchVectorField(null=True)

    class Meta:
        ordering = ("-pub_date",)
        indexes = (GinIndex(fields=["search_vector"]),)

    objects = ArticleManager()

    def __str__(self):
        return self.title


class HighlightedArticle(models.Model):
    highlighted_article_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "article"], name="unique_highlighted"
            )
        ]

    objects = HighlightedArticlesManager()

    def __str__(self):
        return f"{self.user} - {self.article}"


class TrendingTopicContent(models.Model):
    ttopic_id = models.AutoField(primary_key=True)
    article = models.OneToOneField(Article, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.ttopic_id} - {self.article}"


class StockPitch(models.Model):
    stock_pitch_id = models.AutoField(primary_key=True)
    article = models.OneToOneField(Article, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.stock_pitch_id} - {self.article}"
