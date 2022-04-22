# Django imports
from django.urls import path, include
# Local imports
from home.views import (feed, lists, sectors, list_details, main, articles,
                        search_results, sector_details, settings)

app_name = 'home'

urlpatterns = [
    path('feed/', feed, name='feed'),
    path('lists/', lists, name="lists"),
    path('sectors/', sectors, name="sectors"),
    path('articles/', articles, name="articles"),
    path('', main, name="main"),
    path('settings/', settings, name="settings"),
    path('search_results/<str:search_term>',
         search_results,
         name="search-results"),
    path('list/<int:list_id>', list_details, name="list-details"),
    path('sector/<slug:slug>', sector_details, name="sector-details"),
    path('api/', include('home.api.urls', namespace='api')),
]
