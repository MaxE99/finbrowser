from typing import Any, Dict

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from apps.utils import create_paginator
from apps.source.utils import filter_sources
from apps.home.views import BaseMixin
from apps.source.models import Source, SourceRating, SourceTag
from apps.article.models import Article
from apps.home.models import Notification
from apps.sector.models import Sector


class SourceDetailView(DetailView, BaseMixin):
    """
    View to display the details of a specific Source.
    """

    model = Source
    context_object_name = "source"
    template_name = "source/source_profile.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Overrides the context data to add extra context related to the source, such as
        latest content, similar sources, and subscription status.

        Args:
            **kwargs (Any): Additional keyword arguments for context data.

        Returns:
            Dict[str, Any]: Context data for rendering the template.
        """
        context = super().get_context_data(**kwargs)
        source = self.get_object()

        if self.request.user.is_authenticated:
            subscribed = (
                True if self.request.user in source.subscribers.all() else False
            )
            user_rating = SourceRating.objects.get_user_rating(
                self.request.user, source
            )
            context["notification_id"] = (
                Notification.objects.check_source_notification_exists(
                    self.request.user, source
                )
            )
        else:
            subscribed = user_rating = None

        context["latest_content"] = create_paginator(
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
    """
    View to display the ranking of sources based on ratings.
    """

    model = Source
    context_object_name = "source"
    template_name = "source/source_ranking.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Overrides the context data to add extra information such as user ratings, available sectors,
        and search parameters for filtering sources.

        Args:
            **kwargs (Any): Additional keyword arguments for context data.

        Returns:
            Dict[str, Any]: Context data for rendering the template.
        """
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context["user_ratings"] = SourceRating.objects.get_user_ratings_dict(
                self.request.user
            )

        context["sources"] = create_paginator(
            self.request,
            filter_sources(self.request.GET),
            25,
            "page",
        )
        context["sectors"] = Sector.objects.all()
        context["tags"] = SourceTag.objects.all()
        context["search_parameters"] = dict(self.request.GET)
        return context
