# Django imports
from django.urls import path
# Local imports
from apps.home.views import MainView, NotificationView, FeedView, SearchResultView

app_name = 'home'

urlpatterns = [
    path('', MainView.as_view(), name="main"),
    path('feed/', FeedView.as_view(), name='feed'),
    path('notifications/', NotificationView.as_view(), name="notifications"),
    path('search_results/<str:search_term>', SearchResultView.as_view(), name="search-results"),
]
