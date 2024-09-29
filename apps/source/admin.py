from django.contrib import admin

from apps.source.models import Source, SourceRating, SourceTag


class SourceSearch(admin.ModelAdmin):
    """
    Customizes the Django admin interface for the Source model to add search functionality.

    This class enables searching for sources by their name in the admin interface.
    """

    search_fields = [
        "name",
    ]


admin.site.register(Source, SourceSearch)
admin.site.register(SourceRating)
admin.site.register(SourceTag)
