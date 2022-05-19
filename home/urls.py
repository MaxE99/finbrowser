# Django imports
from django.urls import path, include
# Local imports
from home.views import (feed, lists, lists_search, sectors, list_details, main, articles, articles_search,
                        search_results, sector_details, settings)

app_name = 'home'

urlpatterns = [
    path('feed/', feed, name='feed'),
    path('lists/', lists, name="lists"),
    path('lists/<str:timeframe>/<str:content_type>/<str:minimum_rating>/<str:sources>/', lists_search, name="lists-search"),
    path('sectors/', sectors, name="sectors"),
    path('articles/', articles, name="articles"),
    path('articles/<str:timeframe>/<str:sector>/<str:paywall>/<str:sources>/', articles_search, name="articles-search"),
    path('', main, name="main"),
    path('settings/', settings, name="settings"),
    path('search_results/<str:search_term>',
         search_results,
         name="search-results"),
    path('list/<slug:profile_slug>/<slug:list_slug>', list_details, name="list-details"),
    path('sector/<slug:slug>', sector_details, name="sector-details"),
    path('api/', include('home.api.urls', namespace='api')),
]
