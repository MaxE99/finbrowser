# Django imports
from django.db import models

class ArticleManager(models.Manager):

    def get_articles_from_list_sources_and_website(self, list, website):
        return self.filter(source__in=list.sources.all(), source__website=website).select_related('source', 'source__sector', 'tweet_type', 'source__website').order_by('-pub_date')

    def get_articles_from_list_sources_excluding_website(self, list, website):
        return self.filter(source__in=list.sources.all()).select_related('source', 'source__sector', 'source__website').exclude(source__website=website).order_by('-pub_date')

    def filter_articles(self, search_term):
        return self.filter(search_vector=search_term).select_related('source', 'source__sector', 'tweet_type', 'source__website').order_by('-pub_date')

    def get_content_from_source(self, source):
        return self.select_related('source', 'source__sector', 'source__website', 'tweet_type').filter(source=source).order_by('-pub_date')

    def get_content_excluding_website(self, website):
        return self.exclude(source__website=website).select_related('source', 'source__website', 'source__sector').order_by('-pub_date').only('article_id', 'source__favicon_path' ,'source__slug', 'title', 'source__sector__slug', 'source__sector', 'pub_date', 'source__website__logo', 'link', 'source__sector__sector_id', 'source__sector__name')
    
    def get_content_from_website(self, website):
        return self.filter(source__website=website).select_related('source', 'tweet_type').order_by('-pub_date').only('article_id', 'source__favicon_path', 'source__slug', 'source__name', 'title', 'tweet_type__image_path', 'pub_date', 'link', 'source__source_id', 'source__website_id')

    def get_content_from_sector_and_website(self, sector, website):
        return self.select_related('source', 'source__sector', 'tweet_type', 'source__website').filter(source__website=website, source__in=sector.source_set.all()).order_by('-pub_date')

    def get_content_from_sector_excluding_website(self, sector, website):
        return self.select_related('source', 'source__sector', 'source__website', 'tweet_type').filter(source__in=sector.source_set.all()).exclude(source__website=website).order_by('-pub_date')

    def get_subscribed_content_excluding_website(self, sources, website):
        return self.select_related('source', 'source__sector', 'source__website', 'tweet_type').filter(source__in=sources).exclude(source__website=website).order_by('-pub_date')

    def get_subscribed_content_from_website(self, sources, website):
        return self.select_related('source', 'source__sector', 'source__website', 'tweet_type').filter(source__in=sources, source__website=website).order_by('-pub_date')

class HighlightedArticlesManager(models.Manager):

    def get_highlighted_articles_title(self, user):
        highlighted_articles_titles = []
        highlighted_articles = self.select_related('article').filter(user=user)
        for article in highlighted_articles:
            highlighted_articles_titles.append(article.article.title)
        return highlighted_articles_titles

    def get_highlighted_content_of_user(self, user):
        return self.filter(user=user).select_related('article__source', 'article__source__sector', 'article__source__website', 'article__tweet_type').order_by('-article__pub_date')
