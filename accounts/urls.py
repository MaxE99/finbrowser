# Django imports
from django.urls import path
# Local imports
from accounts.views import ProfileView

app_name = 'accounts'

urlpatterns = [
    path('profile/<slug:slug>', ProfileView.as_view(), name="profile"),
]