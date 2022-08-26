# Django imports
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
# Local imports
from apps.article.managers import ArticleManager, HighlightedArticlesManager
from apps.source.models import Source

User = get_user_model()

class TweetType(models.Model):
    TYPE_CHOICES = [('Image', 'Image'), ('Link', 'Link'), ('Retweet', 'Retweet'), ('Basic', 'Basic'), ('Quote', 'Quote'), ('Reply', 'Reply')]
    tweet_type_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='None')
    image_path = models.CharField(max_length=500, blank=True, null=True)
    text = models.CharField(max_length=500, blank=True, null=True)
    pub_date = models.DateTimeField(blank=True, null=True)
    author = models.CharField(max_length=100, blank=True, null=True)
    link = models.CharField(max_length=500, blank=True, null=True)
    initial_tweet_img_path = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f'{self.type} - {self.tweet_type_id}'

class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=500, db_index=True)
    link = models.URLField()
    pub_date = models.DateTimeField()
    source = models.ForeignKey(Source, blank=True, null=True, on_delete=models.CASCADE)
    external_id = models.CharField(unique=True, null=True, blank=True, max_length=100)
    tweet_type = models.ForeignKey(TweetType, blank=True, null=True, on_delete=models.SET_NULL, related_name='tweet')
    search_vector = SearchVectorField(null=True)

    class Meta:
        indexes = (GinIndex(fields=["search_vector"]),)

    objects = ArticleManager()

    def __str__(self):
        return self.title


class HighlightedArticle(models.Model):
    highlighted_article_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)

    objects = HighlightedArticlesManager()

    def __str__(self):
        return f'{self.user} - {self.article}'
