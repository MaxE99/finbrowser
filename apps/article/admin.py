# Django Imports
from django.contrib import admin
# Local imports
from apps.article.models import Article, HighlightedArticle, AudioOfTheWeek, ArticleOfTheWeek, TrendingTopicArticle, EnergyCrisisTweet, MacroTweets, TweetType

admin.site.register(HighlightedArticle)
admin.site.register(Article)
admin.site.register(TweetType)
admin.site.register(AudioOfTheWeek)
admin.site.register(ArticleOfTheWeek)
admin.site.register(TrendingTopicArticle)
admin.site.register(EnergyCrisisTweet)
admin.site.register(MacroTweets)