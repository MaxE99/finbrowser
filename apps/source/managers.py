# Django imports
from django.db import models
from django.db.models import Sum

class SourceManager(models.Manager):

    def filter_by_subscription(self, user):
        return self.filter(subscribers=user).only('favicon_path', 'slug', 'name', 'average_rating')

    def filter_by_search_term(self, search_term):
        return self.filter(name__istartswith=search_term)

    def filter_by_list_and_search_term_exclusive(self, search_term, list):
        return self.filter(name__istartswith=search_term).exclude(source_id__in=list.sources.all())

    def filter_by_subscription_and_search_term_exclusive(self, search_term, user):
        return self.filter(name__istartswith=search_term).exclude(subscribers=user)


class SourceRatingManager(models.Manager):

    def get_user_rating(self, user, source):
        return self.get(user=user, source=source).rating if self.filter(user=user, source=source).exists() else False

    def get_average_rating(self, source):
        list_ratings = self.filter(source=source)
        sum_ratings = self.filter(source=source).aggregate(Sum('rating'))
        sum_ratings = sum_ratings.get("rating__sum", None)
        return round(sum_ratings / list_ratings.count(), 1) if sum_ratings else None

    def get_ammount_of_ratings(self, source):
        return self.filter(source=source).count()

    def save_rating(self, user, source, rating):
        if self.filter(user=user, source=source).exists():
            self.get(user=user, source=source).update(rating=rating)
        else:
            self.create(user=user, source=source, rating=rating)
