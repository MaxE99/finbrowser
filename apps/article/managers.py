# Django imports
from django.shortcuts import get_object_or_404
from django.db import models
# Local imports
from apps.accounts.models import Website

try:
    TWITTER = get_object_or_404(Website, name="Twitter")
except:
    TWITTER = None


class ArticleManager(models.Manager):

    def filter_by_search_term(self, search_term):
        return self.filter(search_vector=search_term).select_related('source', 'source__sector', 'tweet_type', 'source__website')

    def filter_by_list_and_website(self, list, website=TWITTER, website_inclusive=True):
        if website_inclusive:
            return self.filter(source__in=list.sources.all().values_list("source_id", flat=True), source__website=website).select_related('source', 'source__sector', 'tweet_type', 'source__website')
        return self.filter(source__in=list.sources.all().values_list("source_id", flat=True)).exclude(source__website=website).select_related('source', 'source__sector', 'source__website')

    def filter_by_source(self, source):
        return self.filter(source=source).select_related('source', 'source__sector', 'source__website', 'tweet_type')

    def filter_by_sector_and_website(self, sector, website=TWITTER, website_inclusive=True):
        if website_inclusive:
            return self.filter(source__website=website, source__in=sector.source_set.all().values_list("source_id", flat=True)).select_related('source', 'source__sector', 'tweet_type', 'source__website')
        return self.filter(source__in=sector.source_set.all().values_list("source_id", flat=True)).exclude(source__website=website).select_related('source', 'source__sector', 'source__website', 'tweet_type')

    def filter_by_subscription_and_website(self, sources, website=TWITTER, website_inclusive=True):
        if website_inclusive:
            return self.filter(source__in=sources, source__website=website).select_related('source', 'source__sector', 'source__website', 'tweet_type')
        return self.filter(source__in=sources).exclude(source__website=website).select_related('source', 'source__sector', 'source__website', 'tweet_type')


class HighlightedArticlesManager(models.Manager):

    def filter_by_user(self, user):
        return self.filter(user=user).select_related('article__source', 'article__source__sector', 'article__source__website', 'article__tweet_type').order_by('-article__pub_date')

    def get_ids_by_user(self, user):
        return self.filter(user=user).values_list("article", flat=True)

 