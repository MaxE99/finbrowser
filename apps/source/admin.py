# Django Imports
from django.contrib import admin
# Local Imports
from apps.source.models import Source, SourceRating

admin.site.register(Source)
admin.site.register(SourceRating)