# Django Imports
from django.contrib import admin
# Local Imports
from apps.source.models import Source, SourceRating

class SourceSearch(admin.ModelAdmin):
    search_fields = ['name', ]

admin.site.register(Source, SourceSearch)
admin.site.register(SourceRating)