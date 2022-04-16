# Django imports
from django.urls import path
# Local imports
from source.views import profile

app_name = 'source'

urlpatterns = [path('profile/<str:domain>', profile, name='profile')]
