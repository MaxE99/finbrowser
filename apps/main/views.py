# Django imports
from django.views.generic import TemplateView
# Local imports
from apps.logic.pure_logic import paginator_create
from apps.mixins import BaseMixin
from apps.source.models import Source
from apps.article.models import ArticleOfTheWeek, AudioOfTheWeek, EnergyCrisisTweet, MacroTweets, TrendingTopicArticle


class MainView(TemplateView, BaseMixin):
    template_name = 'main/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles_of_the_week'] = paginator_create(self.request, ArticleOfTheWeek.objects.all().select_related('article__source', 'article__source__sector', 'article__source__website').order_by('-article__pub_date'), 10, 'articles_of_the_week')
        context['energy_crisis_tweets'] = paginator_create(self.request, EnergyCrisisTweet.objects.all().select_related('article__source', 'article__source__sector', 'article__source__website').order_by('-article__pub_date'), 10, 'energy_crisis_tweets')
        context['macro_tweets'] = paginator_create(self.request, MacroTweets.objects.all().select_related('article__source', 'article__source__sector', 'article__source__website').order_by('-article__pub_date'), 10, 'macro_tweets')
        context['highest_rated_sources'] = Source.objects.filter(average_rating__gte=4, ammount_of_ratings__gte=2).order_by('average_rating')[:10]
        context['trending_topic_articles'] = paginator_create(self.request, TrendingTopicArticle.objects.all().select_related('article__source', 'article__source__sector', 'article__source__website').order_by('-article__pub_date'), 10, 'trending_topic_articles')
        context['audio_of_the_week'] = paginator_create(self.request, AudioOfTheWeek.objects.all().select_related('article__source', 'article__source__sector', 'article__source__website').order_by('-article__pub_date'), 10, 'audio_of_the_week')
        return context