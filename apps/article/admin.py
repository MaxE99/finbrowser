# Django Imports
from django.contrib import admin
# Local imports
from apps.article.models import Article, HighlightedArticle, AudioOfTheWeek, ArticleOfTheWeek, TrendingTopicArticle, EnergyCrisisTweet, MacroTweets, TweetType

class ArticleSearch(admin.ModelAdmin):
    search_fields = ['title', ]

admin.site.register(HighlightedArticle)
admin.site.register(Article, ArticleSearch)
admin.site.register(TweetType)
admin.site.register(AudioOfTheWeek)
admin.site.register(ArticleOfTheWeek)
admin.site.register(TrendingTopicArticle)
admin.site.register(EnergyCrisisTweet)
admin.site.register(MacroTweets)