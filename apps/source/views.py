# Django import
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.db.models import Q
# Local import
from apps.logic.pure_logic import paginator_create
from apps.home.views import TWITTER, BaseMixin
from apps.source.models import Source, SourceRating, Website, SourceTag
from apps.list.models import List
from apps.article.models import Article
from apps.home.models import Notification
from apps.sector.models import Sector


class SourceDetailView(DetailView, BaseMixin):
    model = Source
    context_object_name = 'source'
    template_name = 'source/source_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        source = self.get_object()
        if self.request.user.is_authenticated:
            subscribed = True if self.request.user in source.subscribers.all() else False
            user_rating = SourceRating.objects.get_user_rating(self.request.user, source)
            notifications_activated = Notification.objects.filter(user=self.request.user, source=source).exists()
        else:
            subscribed = False  
            user_rating = notifications_activated = None
        latest_content = Article.objects.filter_by_source(source)
        if source.website == TWITTER:
            context['links_and_retweets'] = paginator_create(self.request, latest_content.filter(Q(tweet_type__type="Retweet") | Q(tweet_type__type="Link")), 25, 'links_and_retweets')
            context['images'] = paginator_create(self.request, latest_content.filter(tweet_type__type="Image"), 25, 'images')
        context['latest_articles'] = paginator_create(self.request, latest_content, 50, 'latest_content')
        context['lists'] = paginator_create(self.request, List.objects.filter_by_source(source), 50, 'lists')
        context['subscribed'] = subscribed
        context['user_rating'] = user_rating
        context['notifications_activated'] = notifications_activated
        return context


class SourceRankingView(ListView, BaseMixin):
    model = Source
    context_object_name = 'source'
    template_name = 'source/source_ranking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated: 
            context['subscribed_sources'] = Source.objects.filter_by_subscription(self.request.user)
            context['user_ratings'] = SourceRating.objects.filter(user=self.request.user)
        websites = self.request.GET.getlist("website")
        sectors = self.request.GET.getlist("sector")
        tags = self.request.GET.getlist("tag")
        content = self.request.GET.getlist("content")
        paywall = self.request.GET.getlist("paywall")
        top_sources = self.request.GET.getlist("top_sources_only")
        q_objects = Q()
        if len(websites):
            websites = Website.objects.filter(name__in=websites)
            q_objects.add(Q(website__in=websites), Q.AND)
        if len(sectors):
            sectors = Sector.objects.filter(name__in=sectors)
            q_objects.add(Q(sector__in=sectors), Q.AND)
        if len(tags):
            tags = SourceTag.objects.filter(name__in=tags)
            q_objects.add(Q(tags__in=tags), Q.AND)
        if len(content) > 0 and len(content) < 3:
            q_objects.add(Q(content_type__in=content), Q.AND)
        if len(paywall) > 0 and len(content) < 3:
            q_objects.add(Q(paywall__in=paywall), Q.AND)
        if top_sources:
            q_objects.add(Q(top_source=True), Q.AND)
        context['sources'] = paginator_create(self.request, Source.objects.filter(q_objects).order_by("-average_rating"), 25, 'page')
        context['sectors'] = Sector.objects.all()
        context['search_parameters'] = dict(self.request.GET)
        return context