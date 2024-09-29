from django.urls import path

from apps.source.views import SourceDetailView, SourceRankingView

app_name = "source"

urlpatterns = [
    path("source/<slug:slug>", SourceDetailView.as_view(), name="source_profile"),
    path("sources", SourceRankingView.as_view(), name="source_ranking"),
]
