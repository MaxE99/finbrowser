# Django imports
from django.urls import path
# Local imports
from apps.accounts.views import SettingsView, set_timezone

app_name = 'accounts'

urlpatterns = [
    path('profile/settings', SettingsView.as_view(), name="settings"),
    path('set_timezone', set_timezone, name='set_timezone')
]