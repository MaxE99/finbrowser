# Django import
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
# Local imports
from apps.logic.pure_logic import paginator_create
from apps.mixins import BaseMixin
from apps.article.models import Article
from apps.sector.models import Sector
from apps.source.models import Source
from apps.logic.pure_logic import sources_filter


class SectorView(ListView, BaseMixin):
    model = Sector
    context_object_name = 'sectors'
    template_name = 'sector/sectors.html'
    queryset = Sector.objects.prefetch_related('source_set').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sources = Source.objects.all()
        context['results_found'] = sources.count()
        context['filtered_sources'] = sources.values_list('name', flat=True)
        return context


class SectorSearchView(ListView, BaseMixin):
    model = Sector
    context_object_name = 'sectors'
    template_name = 'sector/sectors.html'
    queryset = Sector.objects.prefetch_related('source_set').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered_sources = sources_filter(self.kwargs['paywall'], self.kwargs['type'], self.kwargs['minimum_rating'], self.kwargs['website'], Source.objects.all())
        context['results_found'] = filtered_sources.count()
        context['filtered_sources'] = filtered_sources.values_list('name', flat=True)
        return context


class SectorDetailView(DetailView, BaseMixin):
    model = Sector
    context_object_name = 'sector'
    template_name = 'sector/sector_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sector = self.get_object()
        context['news_sources'] = Source.objects.filter(news=True, sector=sector)
        context['articles_from_sector'] = paginator_create(self.request, Article.objects.filter_by_sector_and_website(sector, website_inclusive=False), 50, 'long_form_content')
        context['tweets_from_sector'] = paginator_create(self.request, Article.objects.filter_by_sector_and_website(sector), 25, 'tweets')
        return context
