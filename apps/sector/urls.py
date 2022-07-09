# Django imports
from django.urls import path
from django.views.decorators.cache import cache_page
# Local imports
from apps.sector.views import SectorDetailView, SectorView

app_name = 'sector'

urlpatterns = [
    path('sector/<slug:slug>', SectorDetailView.as_view(), name="sector-details"),
    path('sectors/', cache_page(86400)(SectorView.as_view()), name="sectors"),
]
