# Django imports
from django.db import models
from django.db.models import Sum


class ListManager(models.Manager):

    def add_articles(self, article, list_ids):
        list_ids = list_ids.split(",")
        for list_id in list_ids:
            list = self.get(list_id=list_id)
            list.articles.add(article)

    def get_created_lists(self, user):
        return self.filter(creator=user).order_by('name')

    def get_highlighted_articles(self, list_id):
        return self.get(list_id=list_id).articles.all().order_by('-pub_date')

    def get_subscribed_lists(self, user):
        return self.filter(subscribers=user).order_by('name')

    def filter_lists(self, search_term):
        return self.filter(name__istartswith=search_term)

    def filter_lists_not_subscribed(self, search_term, user):
        return self.filter(name__istartswith=search_term).exclude(
            creator=user).exclude(subscribers=user).order_by('name')


class SourceManager(models.Manager):

    def add_sources_to_list(self, sources, list):
        sources = sources.split(",")
        for source in sources:
            source = self.get(domain=source)
            list.sources.add(source)

    def get_subscribed_sources(self, user):
        return self.filter(subscribers=user).order_by('name')

    def filter_sources(self, search_term):
        return self.filter(domain__istartswith=search_term).order_by('name')

    def filter_sources_not_in_list(self, search_term, list):
        return self.filter(name__istartswith=search_term).exclude(
            source_id__in=list.sources.all()).order_by('name')

    def filter_sources_not_subscribed(self, search_term, user):
        return self.filter(name__istartswith=search_term).exclude(
            subscribers=user).order_by('name')


class ArticleManager(models.Manager):

    def get_articles_from_subscribed_sources(self, subscribed_sources):
        return self.filter(source__in=subscribed_sources).order_by('-pub_date')

    def get_articles_from_list_sources(self, list):
        return self.filter(source__in=list.sources.all()).order_by('-pub_date')

    def get_articles_from_sector(self, sector):
        return self.filter(
            source__in=sector.sectors.all()).order_by('-pub_date')

    def filter_articles(self, search_term):
        return self.filter(external_source=None).filter(
            title__icontains=search_term).order_by('-pub_date')


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

    def get_ammount_of_ratings(self, list_id):
        return self.filter(list_id=list_id).count()

    def save_rating(self, user, list, rating):
        if self.filter(user=user, list=list).exists():
            list_rating = self.get(user=user, list=list)
            list_rating.rating = rating
            list_rating.save()
        else:
            self.create(user=user, list=list, rating=rating)


class SourceRatingManager(models.Manager):

    def get_user_rating(self, user, source):
        if self.filter(user=user, source=source).exists():
            return self.get(user=user, source=source).rating
        else:
            return False

    def get_average_rating(self, source):
        list_ratings = self.filter(source=source)
        sum_ratings = self.filter(source=source).aggregate(Sum('rating'))
        sum_ratings = sum_ratings.get("rating__sum", None)
        if sum_ratings == None:
            return "None"
        else:
            return round(sum_ratings / len(list_ratings), 1)

    def get_ammount_of_ratings(self, source):
        return self.filter(source=source).count()

    def save_rating(self, user, source, rating):
        if self.filter(user=user, source=source).exists():
            source_rating = self.get(user=user, source=source)
            source_rating.rating = rating
            source_rating.save()
        else:
            self.create(user=user, source=source, rating=rating)
