# Django imports
from django.db import models
from django.db.models import Q


class StockManager(models.Manager):
    def filter_by_search_term(self, search_term):
        if len(search_term) > 2:
            return self.filter(
                Q(ticker__istartswith=search_term)
                | Q(short_company_name__istartswith=search_term)
            ).order_by("ticker")
        return self.filter(ticker__istartswith=search_term).order_by("ticker")
