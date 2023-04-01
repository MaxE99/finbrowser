# Django imports
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


# Local imports
from apps.tests.test_instances import CreateTestInstances
from apps.accounts.forms import (
    EmailAndUsernameChangeForm,
    PasswordChangingForm,
    TimezoneChangeForm,
)

User = get_user_model()


class SettingsView(CreateTestInstances, TestCase):
    def test_settings_view_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/profile/settings")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/settings.html")
        self.assertEqual(response.context["user_source_notifications"].count(), 4)
        self.assertEqual(response.context["user_stock_notifications"].count(), 1)
        self.assertEqual(response.context["user_keyword_notifications"].count(), 2)
        self.assertIsInstance(
            response.context["email_and_name_change_form"], EmailAndUsernameChangeForm
        )
        self.assertIsInstance(
            response.context["change_password_form"], PasswordChangingForm
        )
        self.assertIsInstance(
            response.context["change_timezone_form"], TimezoneChangeForm
        )

    def test_settings_view_anon(self):
        response = self.client.get("/profile/settings", {}, True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "account/login.html")


class TestSettingsViewPostMethods(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="testuser0987", email="testuser0987@test.com"
        )
        self.user.set_password("testpw99")
        self.user.save()

    def test_update_user_valid_post_request(self):
        self.client.login(username="testuser0987", password="testpw99")
        get_response = self.client.get("/profile/settings")
        csrf_token = get_response.context["csrf_token"]
        data = {
            "csrfmiddlewaretoken": csrf_token,
            "changeProfileForm": ["Save"],
            "username": "newusername",
            "email": "newemail@test.com",
        }
        response = self.client.post(reverse("accounts:settings"), data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "newusername")
        self.assertEqual(self.user.email, "newemail@test.com")

    def test_update_user_invalid_post_request(self):
        self.client.login(username="testuser0987", password="testpw99")
        get_response = self.client.get("/profile/settings")
        csrf_token = get_response.context["csrf_token"]
        data = {
            "csrfmiddlewaretoken": csrf_token,
            "changeProfileForm": ["Save"],
            "username": "newusername",
            "email": "",
        }
        response = self.client.post(reverse("accounts:settings"), data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "testuser0987")
        self.assertEqual(self.user.email, "testuser0987@test.com")

    def test_update_timezone_valid_post_request(self):
        self.client.login(username="testuser0987", password="testpw99")
        get_response = self.client.get("/profile/settings")
        csrf_token = get_response.context["csrf_token"]
        data = {
            "timezone": "US/Pacific",
            "csrfmiddlewaretoken": csrf_token,
            "changeProfileForm": ["Save"],
        }
        response = self.client.post(reverse("accounts:settings"), data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.timezone, "US/Pacific")

    def test_update_password_valid_post_request(self):
        self.client.login(username="testuser0987", password="testpw99")
        get_response = self.client.get("/profile/settings")
        csrf_token = get_response.context["csrf_token"]
        data = {
            "csrfmiddlewaretoken": csrf_token,
            "changePasswordForm": ["Save"],
            "old_password": "testpw99",
            "new_password1": "testpw1999",
            "new_password2": "testpw1999",
        }
        self.client.post(reverse("accounts:settings"), data)
        self.client.logout()
        response = self.client.login(username="testuser0987", password="testpw1999")
        self.assertTrue(response)

    def test_update_password_invalid_post_request(self):
        self.client.login(username="testuser0987", password="testpw99")
        get_response = self.client.get("/profile/settings")
        csrf_token = get_response.context["csrf_token"]
        data = {
            "csrfmiddlewaretoken": csrf_token,
            "changePasswordForm": ["Save"],
            "old_password": "testpw99",
            "new_password1": "testpw1999",
            "new_password2": "testpw199",
        }
        self.client.post(reverse("accounts:settings"), data)
        self.client.logout()
        response = self.client.login(username="testuser0987", password="testpw1999")
        self.assertFalse(response)
