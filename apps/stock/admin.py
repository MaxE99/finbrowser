# Django Imports
from django.contrib import admin

# Local Imports
from apps.stock.models import Stock, Portfolio, PortfolioStock, PortfolioKeyword

admin.site.register(Stock)
admin.site.register(Portfolio)
admin.site.register(PortfolioStock)
admin.site.register(PortfolioKeyword)
