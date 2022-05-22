# Django imports
from django.urls import path
# Local imports
from source.views import SourceDetailView

app_name = 'source'

urlpatterns = [path('profile/<slug:slug>', SourceDetailView.as_view(), name='profile')]
