# Django imports
from django.urls import path, include
# Local imports
from home.views import (ListDetailView, SettingsView, ArticleSearchView, ListSearchView, SearchResultView, SectorView, ListsView, ArticleView, MainView, SectorDetailView, FeedView)

app_name = 'home'

urlpatterns = [
    path('feed/', FeedView.as_view(), name='feed'),
    path('lists/', ListsView.as_view(), name="lists"),
    path('lists/<str:timeframe>/<str:content_type>/<str:minimum_rating>/<str:primary_source>/', ListSearchView.as_view(), name="lists-search"),
    path('sectors/', SectorView.as_view(), name="sectors"),
    path('articles/', ArticleView.as_view(), name="articles"),
    path('articles/<str:timeframe>/<str:sector>/<str:paywall>/<str:source>/', ArticleSearchView.as_view(), name="articles-search"),
    path('', MainView.as_view(), name="main"),
    path('settings/', SettingsView.as_view(), name="settings"),
    path('search_results/<str:search_term>', SearchResultView.as_view(), name="search-results"),
    path('list/<slug:profile_slug>/<slug:list_slug>', ListDetailView.as_view(), name="list-details"),
    path('sector/<slug:slug>', SectorDetailView.as_view(), name="sector-details"),
    path('api/', include('api.urls', namespace='api')),
]
