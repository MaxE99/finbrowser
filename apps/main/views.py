# Django imports
from django.views.generic import TemplateView
# Local imports
from apps.mixins import BaseMixin
from apps.source.models import Source
from apps.article.models import ArticleOfTheWeek, AudioOfTheWeek, EnergyCrisisTweet, MacroTweets, TrendingTopicArticle


class FeedView(TemplateView, BaseMixin):
    template_name = 'main/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles_of_the_week'] = ArticleOfTheWeek.objects.all()
        context['energy_crisis_tweets'] = EnergyCrisisTweet.objects.all()
        context['macro_tweets'] = MacroTweets.objects.all()
        context['trending_topic_articles'] = TrendingTopicArticle.objects.all()
        context['highest_rated_sources'] = Source.objects.filter(average_rating__gte=4, ammount_of_ratings__gte=1).order_by('average_rating')[:10]
        context['audio_of_the_week'] = AudioOfTheWeek.objects.all()
        context['newest_sources'] = Source.objects.all()[:10]
        return context