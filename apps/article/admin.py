# Django Imports
from django.contrib import admin
# Local imports
from apps.article.models import Article, HighlightedArticle

admin.site.register(HighlightedArticle)
admin.site.register(Article)