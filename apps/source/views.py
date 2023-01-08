# Django import
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
# Local import
from apps.logic.pure_logic import paginator_create
from apps.home.views import TWITTER, BaseMixin
from apps.source.models import Source, SourceRating
from apps.list.models import List
from apps.article.models import Article
from apps.home.models import Notification
from apps.sector.models import Sector
from django.db.models import Q


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
        context['sources'] = paginator_create(self.request, Source.objects.all().order_by("-average_rating"), 25, 'sources')
        context['sectors'] = Sector.objects.all()
        if self.request.user.is_authenticated: 
            context['subscribed_sources'] = Source.objects.filter_by_subscription(self.request.user)
            context['user_ratings'] = SourceRating.objects.filter(user=self.request.user)
        return context