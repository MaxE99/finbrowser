from typing import Dict, Any

from django.views.generic.detail import DetailView

from apps.utils import create_paginator
from apps.mixins import BaseMixin
from apps.article.models import Article
from apps.sector.models import Sector
from apps.source.models import Source


class SectorDetailView(DetailView, BaseMixin):
    """
    View for displaying details of a specific sector, including related sources
    and articles such as analysis, commentary, and news.
    """

    model = Sector
    context_object_name = "sector"
    template_name = "sector/sector_details.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Retrieves and returns the context data for rendering the template.

        Args:
            **kwargs: Additional keyword arguments to pass to the context.

        Returns:
            Dict[str, Any]: A dictionary containing the context data for the template.
        """

        context = super().get_context_data(**kwargs)
        sources_by_sector = Source.objects.filter_by_sector(self.get_object())

        context["analysis_sources"] = sources_by_sector["analysis_sources"]
        context["commentary_sources"] = sources_by_sector["commentary_sources"]
        context["news_sources"] = sources_by_sector["news_sources"]
        context["analysis"] = create_paginator(
            self.request,
            Article.objects.filter(
                source__in=sources_by_sector["analysis_sources"]
            ).select_related("source", "source__website", "tweet_type"),
            50,
            "analysis",
        )
        context["commentary"] = create_paginator(
            self.request,
            Article.objects.filter(
                source__in=sources_by_sector["commentary_sources"]
            ).select_related("source", "source__website", "tweet_type"),
            50,
            "commentary",
        )
        context["news"] = create_paginator(
            self.request,
            Article.objects.filter(
                source__in=sources_by_sector["news_sources"]
            ).select_related("source", "source__website", "tweet_type"),
            50,
            "news",
        )
        return context
