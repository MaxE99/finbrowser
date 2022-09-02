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
        return self.filter(creator=user).select_related('creator__profile').prefetch_related('articles', 'sources')

    def get_highlighted_content(self, list_id):
        return self.get(list_id=list_id).articles.all().select_related('source', 'source__website', 'source__sector', 'tweet_type')

    def get_subscribed_lists(self, user):
        return self.filter(subscribers=user).select_related('creator__profile').only('list_pic', 'slug', 'name', 'creator__profile')

    def filter_lists(self, search_term):
        return self.filter(name__istartswith=search_term, is_public=True).select_related('creator__profile')

    def filter_lists_not_subscribed(self, search_term, user):
        return self.filter(name__istartswith=search_term, is_public=True).exclude(creator=user).exclude(subscribers=user)

    def get_lists_with_source(self, source):
        return self.filter(sources__source_id=source.source_id, is_public=True).select_related('creator__profile', 'creator')


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
        return "None" if sum_ratings == None else round(sum_ratings /list_ratings.count(), 1)

    def get_ammount_of_ratings(self, list_id):
        return self.filter(list_id=list_id).count()

    def save_rating(self, user, list, rating):
        if self.filter(user=user, list=list).exists():
            self.get(user=user, list=list).update(rating=rating)
        else:
            self.create(user=user, list=list, rating=rating)