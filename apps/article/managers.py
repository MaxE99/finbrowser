# Django imports
from django.db import models

class ArticleManager(models.Manager):

    def get_articles_from_list_sources_and_website(self, list, website):
        return self.filter(source__in=list.sources.all(), source__website=website).select_related('source', 'source__sector', 'tweet_type').order_by('-pub_date')

    def get_articles_from_list_sources_excluding_website(self, list, website):
        return self.filter(source__in=list.sources.all()).select_related('source', 'source__sector', 'source__website').exclude(source__website=website).order_by('-pub_date')

    def filter_articles(self, search_term):
        return self.filter(external_source=None).filter(title__icontains=search_term).select_related('source', 'source__sector', 'tweet_type', 'source__website').order_by('-pub_date')

    def get_content_from_source(self, source):
        return self.select_related('source', 'source__sector', 'source__website', 'tweet_type').filter(source=source).order_by('-pub_date')

    def get_content_excluding_website(self, website):
        return self.select_related('source', 'source__website', 'source__sector').filter(external_source=None).exclude(source__website=website).order_by('-pub_date')
    
    def get_content_from_website(self, website):
        return self.select_related('source', 'tweet_type').filter(source__website=website).order_by('-pub_date')

    def get_content_from_sector_and_website(self, sector, website):
        return self.select_related('source', 'source__sector', 'tweet_type').filter(source__website=website, source__in=sector.source_set.all()).order_by('-pub_date')

    def get_content_from_sector_excluding_website(self, sector, website):
        return self.select_related('source', 'source__sector', 'source__website').filter(source__in=sector.source_set.all()).exclude(source__website=website).order_by('-pub_date')

    def get_subscribed_content_excluding_website(self, sources, website):
        return self.select_related('source', 'source__sector', 'source__website').filter(source__in=sources).order_by('-pub_date').exclude(source__website=website)

    def get_subscribed_content_from_website(self, sources, website):
        return self.select_related('source', 'source__sector', 'source__website', 'tweet_type').filter(source__in=sources, source__website=website).order_by('-pub_date')

class HighlightedArticlesManager(models.Manager):

    def get_highlighted_articles_title(self, user):
        highlighted_articles_titles = []
        highlighted_articles = self.select_related('article').filter(user=user)
        for article in highlighted_articles:
            highlighted_articles_titles.append(article.article.title)
        return highlighted_articles_titles

    def get_highlighted_articles_of_user(self, user):
        return self.filter(user=user).select_related('article__source', 'article__source__sector', 'article__source__website', 'article__tweet_type').order_by('-article__pub_date').only('article__article_id', 'article__source__source_id', 'article__link', 'article__title', 'article__source__sector', 'article__source__website', 'article__source__favicon_path', 'article__pub_date','article__tweet_type__image_path', 'article__source__slug')

    def get_highlighted_articles_from_user_and_website(self, user, website):
        return self.select_related('article', 'article__source', 'article__external_source', 'article__source__sector', 'article__source__website').filter(user=user, article__source__website=website).order_by('-article__pub_date')

    def get_highlighted_articles_from_user_excluding_website(self, user, website):
        return self.select_related('article', 'article__source', 'article__external_source', 'article__source__sector', 'article__source__website').filter(user=user).exclude(article__source__website=website).order_by('-article__pub_date')




