# Django imports
from django.urls import path
# Local imports
from source.views import profile

app_name = 'source'

urlpatterns = [path('profile/', profile, name='source-profile')]
