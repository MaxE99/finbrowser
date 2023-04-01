# Django imports
from django.db import models


class ListManager(models.Manager):
    def filter_by_creator(self, user):
        return (
            self.filter(creator=user)
            .select_related("creator__profile")
            .prefetch_related("articles", "sources")
        )

    def get_highlighted_content(self, selected_list):
        return (
            self.get(list_id=selected_list.list_id)
            .articles.all()
            .select_related("source", "source__website", "source__sector", "tweet_type")
        )
