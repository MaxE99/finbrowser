# Django imports
from django.urls import path
# Local imports
from apps.sector.views import SectorDetailView, SectorView, SectorSearchView

app_name = 'sector'

urlpatterns = [
    path('sector/<slug:slug>', SectorDetailView.as_view(), name="sector-details"),
    path('sectors/<str:paywall>/<str:type>/<str:minimum_rating>/<str:website>/', SectorSearchView.as_view(), name="sectors-search"),
    path('sectors/', SectorView.as_view(), name="sectors"),
]
