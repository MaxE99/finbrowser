# Django imports
from django.urls import path, include
# Local imports
from home.views import (lists_search, articles_search, search_results, settings, SectorView, ListView, ArticleView, MainView, ListDetailView, SectorDetailView, FeedView)

app_name = 'home'

urlpatterns = [
    path('feed/', FeedView.as_view(), name='feed'),
    path('lists/', ListView.as_view(), name="lists"),
    path('lists/<str:timeframe>/<str:content_type>/<str:minimum_rating>/<str:sources>/', lists_search, name="lists-search"),
    path('sectors/', SectorView.as_view(), name="sectors"),
    path('articles/', ArticleView.as_view(), name="articles"),
    path('articles/<str:timeframe>/<str:sector>/<str:paywall>/<str:sources>/', articles_search, name="articles-search"),
    path('', MainView.as_view(), name="main"),
    path('settings/', settings, name="settings"),
    path('search_results/<str:search_term>',
         search_results,
         name="search-results"),
    path('list/<slug:profile_slug>/<slug:list_slug>', ListDetailView.as_view(), name="list-details"),
    path('sector/<slug:slug>', SectorDetailView.as_view(), name="sector-details"),
    path('api/', include('home.api.urls', namespace='api')),
]
