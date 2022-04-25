# Django imports
from django.contrib import admin
# Local imports
from support.models import SourceSuggestion, BugReport, FeatureSuggestion

admin.site.register(SourceSuggestion)
admin.site.register(BugReport)
admin.site.register(FeatureSuggestion)