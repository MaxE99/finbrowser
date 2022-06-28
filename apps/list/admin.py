# Django Imports
from django.contrib import admin
# Local Imports
from apps.list.models import List, ListRating

admin.site.register(List)
admin.site.register(ListRating)