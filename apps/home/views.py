# Django imports
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView
# Local imports
from apps.logic.pure_logic import paginator_create
from apps.base_logger import logger
from apps.mixins import BaseMixin
from apps.accounts.models import Website
from apps.source.models import Source
from apps.list.models import List 
from apps.article.models import Article, HighlightedArticle
from apps.stock.models import Stock
from apps.home.models import NotificationMessage, Notification
from django.contrib.auth.mixins import LoginRequiredMixin

User = get_user_model()

try:
    TWITTER = get_object_or_404(Website, name="Twitter")
except:
    logger.error("Twitter not found! Problem with database")
    TWITTER = None
    

class NotificationView(LoginRequiredMixin, TemplateView, BaseMixin):
    template_name = 'home/notifications.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        NotificationMessage.objects.filter(notification__user=self.request.user).update(user_has_seen=True)
        return context


class FeedView(TemplateView, BaseMixin):
    template_name = 'home/feed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated: 
            subscribed_sources = Source.objects.filter_by_subscription(self.request.user)
            context['notification_sources'] = Notification.objects.filter(user=self.request.user).exclude(source=None).values_list('source', flat=True)
            context['subscribed_lists'] = List.objects.get_subscribed_lists_by_user(self.request.user)
            context['subscribed_sources'] = subscribed_sources
            context['subscribed_content'] = paginator_create(self.request, Article.objects.filter_by_subscription_and_website(subscribed_sources, website_inclusive=False), 50, 'long_form_content')
            context['highlighted_content'] = paginator_create(self.request, HighlightedArticle.objects.filter_by_user(self.request.user), 40, 'highlighted_content')
            context['newest_tweets'] = paginator_create(self.request, Article.objects.filter_by_subscription_and_website(subscribed_sources), 25, 'tweets')
        return context


class SearchResultView(TemplateView, BaseMixin):
    template_name = 'home/search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_term = kwargs['search_term']
        if self.request.user.is_authenticated: 
            context['subscribed_sources'] = Source.objects.filter_by_subscription(self.request.user)
            context['notification_sources'] = Notification.objects.filter(user=self.request.user).exclude(source=None).values_list('source', flat=True)
        context['filtered_stocks'] = paginator_create(self.request, Stock.objects.filter_by_search_term(search_term), 50, 'stocks')
        context['filtered_sources'] = Source.objects.filter_by_search_term(search_term)
        filtered_content = Article.objects.filter_by_search_term(search_term)
        context['filtered_tweets'] = paginator_create(self.request, filtered_content.filter(source__website=TWITTER), 25, 'tweets')
        context['filtered_articles'] = paginator_create(self.request, filtered_content.exclude(source__website=TWITTER), 50, 'long_form_content')     
        return context

