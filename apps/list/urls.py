# Django imports
from django.urls import path
# Local imports
from apps.list.views import ListDetailView, ListView, ListSearchView

app_name = 'list'

urlpatterns = [
    path('lists/', ListView.as_view(), name="lists"),
    path('lists/<str:timeframe>/<str:content_type>/<str:minimum_rating>/<str:primary_source>/', ListSearchView.as_view(), name="lists-search"),
    path('list/<slug:profile_slug>/<slug:list_slug>', ListDetailView.as_view(), name="list-details"),
]
