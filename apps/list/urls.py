# Django imports
from django.urls import path

# Local imports
from apps.list.views import (
    ListDetailView,
    HighlightedContentView,
    SubscribedSourcesView,
    ListView,
)

app_name = "list"

urlpatterns = [
    path("lists", ListView.as_view(), name="lists"),
    path("list/<int:list_id>", ListDetailView.as_view(), name="list-details"),
    path(
        "list/highlighted_content",
        HighlightedContentView.as_view(),
        name="list-highlighted_content",
    ),
    path(
        "list/subscribed_sources",
        SubscribedSourcesView.as_view(),
        name="list-subscribed_sources",
    ),
]
