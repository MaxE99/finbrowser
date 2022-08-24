# Django Imports
from django.contrib import admin
# Local imports
from apps.article.models import Article, HighlightedArticle, TweetType

class ArticleSearch(admin.ModelAdmin):
    search_fields = ['title', ]

class SearchInsteadOfDropdown(admin.ModelAdmin):
    autocomplete_fields = ['article', ]


admin.site.register(HighlightedArticle, SearchInsteadOfDropdown)
admin.site.register(Article, ArticleSearch)
admin.site.register(TweetType)