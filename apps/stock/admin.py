# Django Imports
from django.contrib import admin

# Local Imports
from apps.stock.models import Stock, Portfolio, PortfolioStock, PortfolioKeyword


class StockSearch(admin.ModelAdmin):
    search_fields = [
        "ticker",
    ]


admin.site.register(Stock, StockSearch)
admin.site.register(Portfolio)
admin.site.register(PortfolioStock)
admin.site.register(PortfolioKeyword)
