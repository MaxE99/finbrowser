# Django imports
from django.db import models
from django.db.models import Q
from django.db.models import Value


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
        stocks_with_ticker = self.filter(ticker__istartswith=search_term).annotate(
            sort_order=Value(1)
        )
        if stocks_with_ticker.count() < limit:
            stocks_with_company_name = (
                self.filter(
                    Q(search_vector=search_term)
                    | Q(short_company_name__istartswith=search_term)
                )
                .exclude(stock_id__in=[stock.stock_id for stock in stocks_with_ticker])
                .annotate(sort_order=Value(2))[: limit - stocks_with_ticker.count()]
            )
            return stocks_with_ticker.union(stocks_with_company_name).order_by(
                "sort_order", "ticker"
            )
        return stocks_with_ticker[:limit]
