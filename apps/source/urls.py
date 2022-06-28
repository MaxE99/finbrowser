# Django imports
from django.urls import path
# Local imports
from apps.source.views import SourceDetailView

app_name = 'source'

urlpatterns = [
    path('source/<slug:slug>', SourceDetailView.as_view(), name='source'),
]
