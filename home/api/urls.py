# Django imports
from django.urls import path
from django.urls import path, include
from rest_framework import routers
# Local imports
from home.api.api import (
     FilteredList, FilteredSite, FilteredSourceForLists, SocialLinkViewSet,
    FilteredSource, FilteredSourceForFeed, FilteredListForFeed,
    FilteredArticles, ListViewSet, SourceViewSet, ProfileViewSet, SourceRatingViewSet,
    ListRatingViewSet, HighlightedArticleViewSet, notification_change_source, notification_change_list)

app_name = 'api'

router = routers.DefaultRouter()
router.register('lists', ListViewSet)
router.register('sources', SourceViewSet)
router.register('profiles', ProfileViewSet)
router.register('social_links', SocialLinkViewSet)
router.register('source_ratings', SourceRatingViewSet)
router.register('list_ratings', ListRatingViewSet)
router.register('highlighted_articles', HighlightedArticleViewSet)

urlpatterns = [
    path('search_sources_for_list/<int:list_id>/<str:search_term>',
         FilteredSourceForLists.as_view()),
    path('search_lists/<str:search_term>', FilteredList.as_view()),
    path('search_site/<str:search_term>', FilteredSite.as_view()),
    path('search_sources/<str:search_term>', FilteredSource.as_view()),
    path('filter_sources_from_feed/<str:search_term>',
         FilteredSourceForFeed.as_view()),
    path('filter_lists_from_feed/<str:search_term>',
         FilteredListForFeed.as_view()),
    path('change_source_notification/<int:source_id>',
         notification_change_source),
    path('change_list_notification/<int:list_id>', notification_change_list),
    path('search_articles/<str:search_term>', FilteredArticles.as_view()),
    path('', include(router.urls)),
]