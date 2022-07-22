# Django Imports
from django.contrib import admin
# Local imports
from apps.article.models import Article, HighlightedArticle, AudioOfTheWeek, ArticleOfTheWeek, TrendingTopicArticle, EnergyCrisisTweet, MacroTweets, TweetType

class ArticleSearch(admin.ModelAdmin):
    search_fields = ['title', ]

class SearchInsteadOfDropdown(admin.ModelAdmin):
    autocomplete_fields = ['article', ]


admin.site.register(HighlightedArticle)
admin.site.register(Article, ArticleSearch)
admin.site.register(TweetType)
admin.site.register(AudioOfTheWeek, SearchInsteadOfDropdown)
admin.site.register(ArticleOfTheWeek, SearchInsteadOfDropdown)
admin.site.register(TrendingTopicArticle, SearchInsteadOfDropdown)
admin.site.register(EnergyCrisisTweet, SearchInsteadOfDropdown)
admin.site.register(MacroTweets, SearchInsteadOfDropdown)