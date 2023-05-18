# Django imports
from django.db import models
from django.db.models import Q


class StockManager(models.Manager):
    def filter_by_search_term(self, search_term):
        if len(search_term) > 2:
            return self.filter(
                Q(ticker__istartswith=search_term)
                | Q(search_vector=search_term)
                | Q(short_company_name__istartswith=search_term)
            ).order_by("ticker")
        return self.filter(ticker__istartswith=search_term).order_by("ticker")

    def filter_by_search_term_search(self, search_term, limit):
        stocks_with_ticker = self.filter(ticker__istartswith=search_term)
        if stocks_with_ticker.count() < limit:
            stocks_with_company_name = self.filter(
                Q(search_vector=search_term)
                | Q(short_company_name__istartswith=search_term)
            )[: limit - stocks_with_ticker.count()]
            return stocks_with_ticker.union(stocks_with_company_name)
        return stocks_with_ticker[:limit]
