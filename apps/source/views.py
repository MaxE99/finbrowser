# Django import
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

# Local import
from apps.logic.pure_logic import paginator_create
from apps.logic.selectors import filter_sources
from apps.home.views import BaseMixin
from apps.source.models import Source, SourceRating
from apps.article.models import Article
from apps.home.models import Notification
from apps.sector.models import Sector


class SourceDetailView(DetailView, BaseMixin):
    model = Source
    context_object_name = "source"
    template_name = "source/source_profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        source = self.get_object()
        if self.request.user.is_authenticated:
            subscribed = (
                True if self.request.user in source.subscribers.all() else False
            )
            user_rating = SourceRating.objects.get_user_rating(
                self.request.user, source
            )
            context[
                "notification_id"
            ] = Notification.objects.check_source_notification_exists(
                self.request.user, source
            )
        else:
            subscribed = user_rating = None
        context["latest_content"] = paginator_create(
            self.request, Article.objects.filter_by_source(source), 25, "latest_content"
        )
        context["similiar_sources"] = Source.objects.filter(
            source_id__in=source.sim_sources.all()
        ).select_related("sector")
        context["subscribed"] = subscribed
        context["user_rating"] = user_rating
        context["source_ranking"] = (
            Source.objects.filter(average_rating__gt=source.average_rating).count() + 1
        )
        return context


class SourceRankingView(ListView, BaseMixin):
    model = Source
    context_object_name = "source"
    template_name = "source/source_ranking.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["user_ratings"] = SourceRating.objects.get_user_ratings_dict(
                self.request.user
            )
        print(len(filter_sources(self.request.GET)))
        context["sources"] = paginator_create(
            self.request,
            filter_sources(self.request.GET),
            25,
            "page",
        )
        context["sectors"] = Sector.objects.all()
        context["search_parameters"] = dict(self.request.GET)
        return context
