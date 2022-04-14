# Django imports
from django.contrib import admin
# Local imports
from home.models import Source, List, Sector, SourceRating, ListRating, HighlightedArticle, Article

admin.site.register(Source)
admin.site.register(List)
admin.site.register(Sector)
admin.site.register(SourceRating)
admin.site.register(ListRating)
admin.site.register(HighlightedArticle)
admin.site.register(Article)