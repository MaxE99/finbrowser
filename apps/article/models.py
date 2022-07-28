# Django imports
from django.db import models
from django.contrib.auth import get_user_model
# Local imports
from apps.article.managers import ArticleManager, HighlightedArticlesManager
from apps.source.models import Source

User = get_user_model()

class TweetType(models.Model):
    TYPE_CHOICES = [('Image', 'Image'), ('Link', 'Link'), ('Retweet', 'Retweet'), ('Basic', 'Basic')]
    tweet_type_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='None')
    image_path = models.CharField(max_length=500, blank=True, null=True)
    link = models.CharField(max_length=500, blank=True, null=True)

class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=500, db_index=True)
    link = models.URLField()
    pub_date = models.DateTimeField()
    source = models.ForeignKey(Source, blank=True, null=True, on_delete=models.SET_NULL)
    external_id = models.CharField(unique=True, null=True, blank=True, max_length=100)
    tweet_type = models.ForeignKey(TweetType, blank=True, null=True, on_delete=models.SET_NULL)

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


class ArticleOfTheWeek(models.Model):
    arotw_id = models.AutoField(primary_key=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'Article of the week - {self.article}'

class AudioOfTheWeek(models.Model):
    auotw_id = models.AutoField(primary_key=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'Audio of the week - {self.article}'

class TrendingTopicArticle(models.Model):
    tta_id = models.AutoField(primary_key=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)  

    def __str__(self):
        return f'Trending Topic - {self.article}'    

class EnergyCrisisTweet(models.Model):
    ect_id = models.AutoField(primary_key=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'Energy Crisis Tweet - {self.article}'

class MacroTweets(models.Model):
    mt_id = models.AutoField(primary_key=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'Macro Tweet - {self.article}'