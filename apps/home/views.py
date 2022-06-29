# Django imports
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
# Local imports
from apps.logic.pure_logic import paginator_create
from apps.base_logger import logger
from apps.mixins import BaseMixin, AddExternalArticleFormMixin, CreateListFormMixin
from apps.list.models import List
from apps.accounts.models import Website
from apps.source.models import Source
from apps.list.models import List 
from apps.article.models import Article, HighlightedArticle


User = get_user_model()

try:
    TWITTER = get_object_or_404(Website, name="Twitter")
except:
    logger.error("Twitter not found! Problem with database")
    TWITTER = None

# Mixins:

class MainView(TemplateView, BaseMixin):
    template_name = 'home/main.html'


class NotificationView(TemplateView, BaseMixin):
    template_name = 'home/notifications.html'


class FeedView(TemplateView, LoginRequiredMixin, BaseMixin, AddExternalArticleFormMixin):
    template_name = 'home/feed.html'

    def post(self, request, *args, **kwargs):
        if 'createListForm' in request.POST:
            post_res = CreateListFormMixin.post(self, request, multi_form_page=True)
            if post_res == 'Failed':
                return redirect('home:feed')
            else:
                profile_slug, list_slug = post_res
                return redirect('list:list-details', profile_slug=profile_slug, list_slug=list_slug)
        elif 'addExternalArticlesForm' in request.POST:
            AddExternalArticleFormMixin.post(self, request)
            return redirect('home:feed')
        else:
            logger.error(f"Feed view problems with POST request! - {request.POST}")
            return HttpResponseRedirect(self.request.path_info)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subscribed_sources = Source.objects.get_subscribed_sources(self.request.user)
        context['subscribed_lists'] = List.objects.get_subscribed_lists(self.request.user)
        context['subscribed_sources'] = subscribed_sources
        context['subscribed_content'] = paginator_create(self.request, Article.objects.get_subscribed_content_excluding_website(subscribed_sources, TWITTER), 10, 'subscribed_content')
        context['highlighted_content'] = paginator_create(self.request, HighlightedArticle.objects.get_highlighted_articles_from_user_excluding_website(self.request.user, TWITTER), 10, 'highlighted_content')
        context['highlighted_tweets'] = paginator_create(self.request, HighlightedArticle.objects.get_highlighted_articles_from_user_and_website(self.request.user, TWITTER), 10, 'highlighted_tweets')
        context['newest_tweets'] = paginator_create(self.request, Article.objects.get_subscribed_content_from_website(subscribed_sources, TWITTER), 10, 'newest_tweets')
        return context


class SearchResultView(TemplateView, BaseMixin):
    template_name = 'home/search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_term = kwargs['search_term']
        context['filtered_lists'] = paginator_create(self.request, List.objects.filter_lists(search_term), 10, 'filtered_lists')
        context['filtered_sources'] = Source.objects.filter_sources(search_term)
        context['filtered_articles'] = paginator_create(self.request, Article.objects.filter_articles(search_term), 10, 'filtered_articles')
        return context






