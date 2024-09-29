from django.urls import path

from apps.sector.views import SectorDetailView

app_name = "sector"

urlpatterns = [
    path("sector/<slug:slug>", SectorDetailView.as_view(), name="sector-details"),
]
