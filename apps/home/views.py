# Django imports
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
# Local imports
from apps.logic.pure_logic import paginator_create
from apps.base_logger import logger
from apps.mixins import BaseMixin
from apps.accounts.models import Website
from apps.source.models import Source
from apps.list.models import List 
from apps.article.models import Article, HighlightedArticle
from apps.stock.models import Stock

User = get_user_model()

try:
    TWITTER = get_object_or_404(Website, name="Twitter")
except:
    logger.error("Twitter not found! Problem with database")
    TWITTER = None
    

class NotificationView(TemplateView, BaseMixin):
    template_name = 'home/notifications.html'


class FeedView(TemplateView, LoginRequiredMixin, BaseMixin):
    template_name = 'home/feed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subscribed_sources = Source.objects.get_subscribed_sources(self.request.user)
        context['subscribed_lists'] = List.objects.get_subscribed_lists(self.request.user)
        context['subscribed_sources'] = subscribed_sources
        context['subscribed_content'] = paginator_create(self.request, Article.objects.get_subscribed_content_excluding_website(subscribed_sources, TWITTER), 20, 'subscribed_content')
        context['highlighted_content'] = paginator_create(self.request, HighlightedArticle.objects.get_highlighted_content_of_user(self.request.user), 10, 'highlighted_content')
        context['newest_tweets'] = paginator_create(self.request, Article.objects.get_subscribed_content_from_website(subscribed_sources, TWITTER), 10, 'newest_tweets')
        return context


class SearchResultView(TemplateView, BaseMixin):
    template_name = 'home/search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_term = kwargs['search_term']
        context['filtered_stocks'] = paginator_create(self.request, Stock.objects.filter_stocks(search_term), 20, 'filtered_stocks')
        context['filtered_sources'] = Source.objects.filter_sources(search_term)
        filtered_content = Article.objects.filter_articles(search_term)
        filtered_tweets = filtered_content.filter(source__website=TWITTER).select_related('source', 'source__sector', 'tweet_type', 'source__website').order_by('-pub_date')
        context['filtered_tweets'] = paginator_create(self.request, filtered_tweets, 10, 'filtered_tweets')
        context['filtered_articles'] = paginator_create(self.request, filtered_content.exclude(source__website=TWITTER), 20, 'filtered_articles')
        return context

