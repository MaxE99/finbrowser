# Django imports
from django.urls import path
from django.urls import path, include
from rest_framework import routers
# Local imports
from apps.api.api import (
     FilteredSite, FilteredArticles, ListViewSet, NotificationViewSet,
     SourceViewSet, ProfileViewSet, SourceRatingViewSet, ListRatingViewSet, 
     HighlightedArticleViewSet, FilteredLists, FilteredSources, SourceTagViewSet, add_sources_to_list, subscribe_to_sources, change_source_status_from_lists)

app_name = 'api'

router = routers.DefaultRouter()
router.register('lists', ListViewSet)
router.register('sources', SourceViewSet)
router.register('profiles', ProfileViewSet)
router.register('source_ratings', SourceRatingViewSet)
router.register('list_ratings', ListRatingViewSet)
router.register('highlighted_articles', HighlightedArticleViewSet)
router.register('notifications', NotificationViewSet)
router.register('source_tags', SourceTagViewSet)

urlpatterns = [
    path('lists/change_source_status_from_lists/', change_source_status_from_lists),
    path('lists/<int:list_id>/add_sources/<str:source_ids>/', add_sources_to_list),
    path('sources/subscribe_to_sources/<str:source_ids>/', subscribe_to_sources),
    path('search_site/<str:search_term>', FilteredSite.as_view()),
    path('search_articles/<str:search_term>', FilteredArticles.as_view()),
    path('search_lists/<str:search_term>', FilteredLists.as_view()),
    path('search_sources/<str:search_term>', FilteredSources.as_view()),
    path('', include(router.urls)),
]