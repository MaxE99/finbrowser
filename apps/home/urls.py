# Django imports
from django.urls import path
# Local imports
from apps.home.views import NotificationView, FeedView, SearchResultView, NewPageView

app_name = 'home'

urlpatterns = [
    path('', FeedView.as_view(), name='feed'),
    # path('new_page', NewPageView.as_view(), name="new_page"),
    path('notifications/', NotificationView.as_view(), name="notifications"),
    path('search_results/<str:search_term>', SearchResultView.as_view(), name="search-results"),
]
