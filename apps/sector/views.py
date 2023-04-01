# Django import
from django.views.generic.detail import DetailView

# Local imports
from apps.logic.pure_logic import paginator_create
from apps.mixins import BaseMixin
from apps.article.models import Article
from apps.sector.models import Sector
from apps.source.models import Source


class SectorDetailView(DetailView, BaseMixin):
    model = Sector
    context_object_name = "sector"
    template_name = "sector/sector_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sources_by_sector = Source.objects.filter_by_sector(self.get_object())
        context["analysis_sources"] = sources_by_sector["analysis_sources"]
        context["commentary_sources"] = sources_by_sector["commentary_sources"]
        context["news_sources"] = sources_by_sector["news_sources"]
        context["analysis"] = paginator_create(
            self.request,
            Article.objects.filter(
                source__in=sources_by_sector["analysis_sources"]
            ).select_related("source", "source__website", "tweet_type"),
            50,
            "analysis",
        )
        context["commentary"] = paginator_create(
            self.request,
            Article.objects.filter(
                source__in=sources_by_sector["commentary_sources"]
            ).select_related("source", "source__website", "tweet_type"),
            50,
            "commentary",
        )
        context["news"] = paginator_create(
            self.request,
            Article.objects.filter(
                source__in=sources_by_sector["news_sources"]
            ).select_related("source", "source__website", "tweet_type"),
            50,
            "news",
        )
        return context
