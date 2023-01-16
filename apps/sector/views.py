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
from apps.home.models import Notification


class SectorView(ListView, BaseMixin):
    model = Sector
    context_object_name = 'sectors'
    template_name = 'sector/sectors.html'
    queryset = Sector.objects.prefetch_related('source_set').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sources = Source.objects.all()
        if self.request.user.is_authenticated:
            context['subscribed_sources'] = Source.objects.filter_by_subscription(self.request.user)
            context['notification_sources'] = Notification.objects.filter(user=self.request.user).exclude(source=None).values_list('source', flat=True)
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
        if self.request.user.is_authenticated:
            context['subscribed_sources'] = Source.objects.filter_by_subscription(self.request.user)
            context['notification_sources'] = Notification.objects.filter(user=self.request.user).exclude(source=None).values_list('source', flat=True)
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
        if self.request.user.is_authenticated:
            context['subscribed_sources'] = Source.objects.filter_by_subscription(self.request.user)
            context['notification_sources'] = Notification.objects.filter(user=self.request.user).exclude(source=None).values_list('source', flat=True)
        # context['news_sources'] = Source.objects.filter(news=True, sector=sector)
        analysis_sources = Source.objects.filter(content_type="Analysis", sector=sector)
        commentary_sources = Source.objects.filter(content_type="Commentary", sector=sector)
        news_sources = Source.objects.filter(content_type = "News", sector=sector)
        context['analysis_content'] = paginator_create(self.request, Article.objects.filter(source__in=analysis_sources), 50, 'analysis_content')
        context['commentary_content'] = paginator_create(self.request, Article.objects.filter(source__in=commentary_sources), 50, 'commentary_content')
        context['news_content'] = paginator_create(self.request, Article.objects.filter(source__in=news_sources), 50, 'news_content')
        return context
