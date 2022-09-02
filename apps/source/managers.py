# Django imports
from django.db import models
from django.db.models import Sum

class SourceManager(models.Manager):

    def get_subscribed_sources(self, user):
        return self.filter(subscribers=user).only('favicon_path', 'slug', 'name')

    def filter_sources(self, search_term):
        return self.filter(name__istartswith=search_term)

    def filter_sources_not_in_list(self, search_term, list):
        return self.filter(name__istartswith=search_term).exclude(source_id__in=list.sources.all())

    def filter_sources_not_subscribed(self, search_term, user):
        return self.filter(name__istartswith=search_term).exclude(subscribers=user)


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
        return None if sum_ratings == None else round(sum_ratings / list_ratings.count(), 1)

    def get_ammount_of_ratings(self, source):
        return self.filter(source=source).count()

    def save_rating(self, user, source, rating):
        if self.filter(user=user, source=source).exists():
            self.get(user=user, source=source).update(rating=rating)
        else:
            self.create(user=user, source=source, rating=rating)
