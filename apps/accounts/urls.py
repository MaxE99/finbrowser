from django.urls import path

from apps.accounts.views import SettingsView

app_name = "accounts"

urlpatterns = [
    path("profile/settings", SettingsView.as_view(), name="settings"),
]
