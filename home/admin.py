# Django imports
from django.contrib import admin
# Local imports
from home.models import Source, List, Sector

admin.site.register(Source)
admin.site.register(List)
admin.site.register(Sector)