from django.urls import path

from apps.home.views import (
    NotificationView,
    FeedView,
    SearchResultView,
    GuideView,
    FaviconView,
)

app_name = "home"

urlpatterns = [
    path("", FeedView.as_view(), name="feed"),
    path("notifications/", NotificationView.as_view(), name="notifications"),
    path(
        "search_results/<str:search_term>",
        SearchResultView.as_view(),
        name="search-results",
    ),
    path("guide/", GuideView.as_view(), name="guide"),
    path("favicon.ico", FaviconView.as_view(), name="favicon"),
]
