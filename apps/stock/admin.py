# Django Imports
from django.contrib import admin
# Local Imports
from apps.stock.models import Stock

admin.site.register(Stock)
