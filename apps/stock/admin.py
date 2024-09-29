from django.contrib import admin

from apps.stock.models import Stock, Portfolio, PortfolioStock, PortfolioKeyword


class StockSearch(admin.ModelAdmin):
    """
    Admin view for searching stocks in the admin interface.
    """

    search_fields = [
        "ticker",
    ]


admin.site.register(Stock, StockSearch)
admin.site.register(Portfolio)
admin.site.register(PortfolioStock)
admin.site.register(PortfolioKeyword)
