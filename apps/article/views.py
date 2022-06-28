# Django imports
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
# Local imports
from apps.logic.pure_logic import paginator_create, articles_filter
from apps.base_logger import logger
from apps.mixins import BaseMixin
from apps.accounts.models import Website
from apps.article.models import Article
from apps.sector.models import Sector


try:
    TWITTER = get_object_or_404(Website, name="Twitter")
except:
    logger.error("Twitter not found! Problem with database")
    TWITTER = None


class ArticleView(ListView, BaseMixin):
    model = Article
    template_name = 'home/articles.html'
    paginate_by = 10

    def get_queryset(self):
        return Article.objects.get_content_excluding_website(TWITTER)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tweets_qs = Article.objects.get_content_from_website(TWITTER)
        context['articles'] = paginator_create(self.request, self.get_queryset(), 10, 'articles')
        context['sectors'] = Sector.objects.all().order_by('name')
        context['tweets'] = paginator_create(self.request, tweets_qs, 20, 'tweets')
        context['results_found'] = self.object_list.count() + tweets_qs.count()
        return context


class ArticleSearchView(ListView, BaseMixin):
    model = Article
    template_name = 'home/articles.html'
    paginate_by = 10

    def get_queryset(self):
        sector = get_object_or_404(Sector, name=self.kwargs['sector']).sector_id if self.kwargs['sector'] != "All" else "All"
        source = get_object_or_404(Website, name=self.kwargs['source']).id if self.kwargs['source'] != "All" else "All"
        return articles_filter(self.kwargs['timeframe'], sector, self.kwargs['paywall'], source, Article.objects.select_related('source').filter(external_source=None))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        articles_qs = self.get_queryset().select_related('source', 'source__website', 'source__sector').filter(external_source=None).exclude(source__website=TWITTER).order_by('-pub_date')
        tweets_qs = self.get_queryset().select_related('source').filter(source__website=TWITTER).order_by('-pub_date')
        context['sectors'] = Sector.objects.all().order_by('name')
        context['articles'] = paginator_create(self.request, articles_qs, 10, 'articles')
        context['tweets'] = paginator_create(self.request, tweets_qs, 20, 'tweets')
        context['results_found'] = articles_qs.count() + tweets_qs.count()
        return context
