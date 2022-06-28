# Django imports
from django.urls import path
# Local imports
from apps.sector.views import SectorDetailView, SectorView

app_name = 'sector'

urlpatterns = [
    path('sector/<slug:slug>', SectorDetailView.as_view(), name="sector-details"),
    path('sectors/', SectorView.as_view(), name="sectors"),
]
