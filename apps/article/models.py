# Django imports
from django.db import models
from django.contrib.auth import get_user_model
# Local imports
from apps.article.managers import ArticleManager, HighlightedArticlesManager
from apps.source.models import Source, ExternalSource

User = get_user_model()

class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=500)
    link = models.URLField()
    pub_date = models.DateTimeField()
    source = models.ForeignKey(Source, blank=True, null=True, on_delete=models.SET_NULL)
    external_source = models.ForeignKey(ExternalSource, blank=True,
                                        null=True,
                                        on_delete=models.SET_NULL)
    external_id = models.CharField(unique=True, null=True, blank=True, max_length=100)

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