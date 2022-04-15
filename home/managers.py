# Django imports
from django.db import models
from django.db.models import Sum


class ListManager(models.Manager):

    def get_created_lists(self, user):
        return self.filter(creator=user).order_by('name')

    def get_subscribed_lists(self, user):
        return self.filter(subscribers=user).order_by('name')

    def filter_lists(self, search_term):
        return self.filter(name__istartswith=search_term)


class SourceManager(models.Manager):

    def get_subscribed_sources(self, user):
        return self.filter(subscribers=user).order_by('name')

    def filter_sources(self, search_term):
        return self.filter(domain__istartswith=search_term)


class ArticleManager(models.Manager):

    def get_articles_from_subscribed_sources(self, subscribed_sources):
        return self.filter(source__in=subscribed_sources).order_by('-pub_date')

    def get_articles_from_list_sources(self, list):
        return self.filter(source__in=list.sources.all()).order_by('-pub_date')

    def filter_articles(self, search_term):
        return self.filter(title__icontains=search_term)


class HighlightedArticlesManager(models.Manager):

    def get_highlighted_articles_title(self, user):
        highlighted_articles_titles = []
        highlighted_articles = self.filter(user=user)
        for article in highlighted_articles:
            highlighted_articles_titles.append(article.article.title)
        return highlighted_articles_titles


class ListRatingManager(models.Manager):

    def get_user_rating(self, user, list_id):
        if self.filter(user=user, list_id=list_id).exists():
            return self.get(user=user, list_id=list_id).rating
        else:
            return False

    def get_average_rating(self, list_id):
        list_ratings = self.filter(list_id=list_id)
        sum_ratings = self.filter(list_id=list_id).aggregate(Sum('rating'))
        sum_ratings = sum_ratings.get("rating__sum", None)
        if sum_ratings == None:
            return "None"
        else:
            return round(sum_ratings / len(list_ratings), 1)