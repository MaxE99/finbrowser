# Django imports
from django.urls import path
from django.urls import path, include
from rest_framework import routers
# Local imports
from home.api.api import (
     FilteredSite, SocialLinkViewSet, FilteredArticles, ListViewSet, NotificationViewSet,
     SourceViewSet, ProfileViewSet, SourceRatingViewSet, ListRatingViewSet, 
     HighlightedArticleViewSet, FilteredLists)

app_name = 'api'

router = routers.DefaultRouter()
router.register('lists', ListViewSet)
router.register('sources', SourceViewSet)
router.register('profiles', ProfileViewSet)
router.register('social_links', SocialLinkViewSet)
router.register('source_ratings', SourceRatingViewSet)
router.register('list_ratings', ListRatingViewSet)
router.register('highlighted_articles', HighlightedArticleViewSet)
router.register('notifications', NotificationViewSet)

urlpatterns = [
    path('search_site/<str:search_term>', FilteredSite.as_view()),
    path('search_articles/<str:search_term>', FilteredArticles.as_view()),
    path('search_lists/<str:search_term>', FilteredLists.as_view()),
    path('', include(router.urls)),
]