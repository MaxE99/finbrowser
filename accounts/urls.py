# Django imports
from django.urls import path
# Local imports
from accounts.views import profile

app_name = 'accounts'

urlpatterns = [
    path('profile/<slug:slug>', profile, name="profile"),
]