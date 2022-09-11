# Django imports
from django.urls import path
# Local imports
from apps.accounts.views import SettingsView

app_name = 'accounts'

urlpatterns = [
    path('profile/settings', SettingsView.as_view(), name="settings"),
]