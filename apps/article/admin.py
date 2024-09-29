from django.contrib import admin

from apps.article.models import (
    Article,
    HighlightedArticle,
    TweetType,
    TrendingTopicContent,
    StockPitch,
)


class ArticleSearch(admin.ModelAdmin):
    """
    Admin view for searching Articles.

    This admin class enables searching Articles by their title
    and provides a filter option by source.
    """

    search_fields = [
        "title",
    ]
    list_filter = [
        "source",
    ]


class SearchInsteadOfDropdown(admin.ModelAdmin):
    """
    Admin view with autocomplete for Article selection.

    This admin class enables the use of an autocomplete field
    for selecting articles.
    """

    autocomplete_fields = [
        "article",
    ]


class StockPitchDropdown(admin.ModelAdmin):
    """
    Admin view for stock pitches with an autocomplete feature.

    This admin class provides an autocomplete selection for articles.
    """

    autocomplete_fields = ["article"]


admin.site.register(HighlightedArticle, SearchInsteadOfDropdown)
admin.site.register(Article, ArticleSearch)
admin.site.register(TweetType)
admin.site.register(TrendingTopicContent, SearchInsteadOfDropdown)
admin.site.register(StockPitch, StockPitchDropdown)
