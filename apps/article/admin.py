# Django Imports
from django.contrib import admin

# Local imports
from apps.article.models import (
    Article,
    HighlightedArticle,
    TweetType,
    TrendingTopicContent,
    StockPitch,
)


class ArticleSearch(admin.ModelAdmin):
    search_fields = [
        "title",
    ]
    list_filter = [
        "source",
    ]


class SearchInsteadOfDropdown(admin.ModelAdmin):
    autocomplete_fields = [
        "article",
    ]


class StockPitchDropdown(admin.ModelAdmin):
    autocomplete_fields = ["article"]


admin.site.register(HighlightedArticle, SearchInsteadOfDropdown)
admin.site.register(Article, ArticleSearch)
admin.site.register(TweetType)
admin.site.register(TrendingTopicContent, SearchInsteadOfDropdown)
admin.site.register(StockPitch, StockPitchDropdown)
