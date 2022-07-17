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
    template_name = 'article/articles.html'
    paginate_by = 10

    def get_queryset(self):
        return Article.objects.all().select_related('source', 'source__website', 'source__sector', 'tweet_type').order_by('-pub_date').only('article_id', 'source__favicon_path', 'source__slug', 'source__name', 'title', 'tweet_type__image_path', 'pub_date', 'link', 'source__source_id', 'source__website_id', 'source__sector__slug', 'source__sector', 'source__website__logo', 'source__sector__sector_id', 'source__sector__name', 'source__url')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tweets_qs = self.get_queryset().filter(source__website=TWITTER)
        articles = self.get_queryset().exclude(source__website=TWITTER)
        context['articles'] = paginator_create(self.request, articles , 20, 'articles')
        context['sectors'] = Sector.objects.all().order_by('name')
        context['tweets'] = paginator_create(self.request, tweets_qs, 10, 'tweets')
        context['results_found'] = self.get_queryset().count()
        return context


class ArticleSearchView(ListView, BaseMixin):
    model = Article
    template_name = 'article/articles.html'
    paginate_by = 10

    def get_queryset(self):
        sector = get_object_or_404(Sector, name=self.kwargs['sector']).sector_id if self.kwargs['sector'] != "All" else "All"
        source = get_object_or_404(Website, name=self.kwargs['source']).website_id if self.kwargs['source'] != "All" else "All"
        return articles_filter(self.kwargs['timeframe'], sector, self.kwargs['paywall'], source, Article.objects.select_related('source').filter(external_source=None))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        tweets_qs = qs.filter(source__website=TWITTER).select_related('source', 'tweet_type')
        articles_qs = qs.exclude(source__website=TWITTER).select_related('source', 'source__website', 'source__sector')
        context['sectors'] = Sector.objects.all().order_by('name')
        context['articles'] = paginator_create(self.request, articles_qs, 10, 'articles')
        context['tweets'] = paginator_create(self.request, tweets_qs, 20, 'tweets')
        context['results_found'] = qs.count()
        return context
