# Django imports
from django.db import models
from django.db.models import Q

class StockManager(models.Manager):

    def filter_by_search_term(self, search_term):
        return self.filter(Q(ticker__istartswith=search_term) | Q(full_company_name__istartswith=search_term)).order_by('full_company_name')