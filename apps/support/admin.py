# Django Imports
from django.contrib import admin
# Local Imports
from apps.support.models import SourceSuggestion, BugReport, FeatureSuggestion

admin.site.register(SourceSuggestion)
admin.site.register(BugReport)
admin.site.register(FeatureSuggestion)