# Django imports
from django.test import TestCase

# Local imports
from apps.accounts.forms import (
    UserCreationForm,
    EmailAndUsernameChangeForm,
    PasswordChangingForm,
    TimezoneChangeForm,
)
from apps.tests.test_instances import CreateTestInstances
from django.contrib.auth import get_user_model

User = get_user_model()


class UserCreationFormTest(CreateTestInstances, TestCase):
    def setUp(self):
        self.valid_data = {
            "username": "johndoe",
            "email": "johndoe@example.com",
            "password1": "mypassword",
            "password2": "mypassword",
        }
        self.invalid_data = {
            "username": "janedoe",
            "email": "janedoe@example.com",
            "password1": "mypassword",
            "password2": "anotherpassword",
        }

    def test_valid_form(self):
        form = UserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form = UserCreationForm(data=self.invalid_data)
        self.assertFalse(form.is_valid())

    def test_clean_password2(self):
        form = UserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.clean_password2(), "mypassword")

    def test_save_method(self):
        form = UserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "johndoe")
        self.assertEqual(user.email, "johndoe@example.com")
        self.assertTrue(user.check_password("mypassword"))

    def test_wrong_second_password(self):
        form = UserCreationForm(
            data={
                "username": "TestUser",
                "email": "testuser@mail.com",
                "password1": "true1234",
                "password2": "wrong1234",
            }
        )
        self.assertEqual(form.errors["password2"], ["Passwords don't match"])

    def test_username_already_exists(self):
        form = UserCreationForm(
            data={
                "username": "TestUser1",
                "email": "testuser@mail.com",
                "password1": "true1234",
                "password2": "true1234",
            }
        )
        self.assertEqual(
            form.errors["username"], ["User with this Username already exists."]
        )

    def test_email_already_exists(self):
        form = UserCreationForm(
            data={
                "username": "TestUser150",
                "email": "testuser1@mail.com",
                "password1": "true1234",
                "password2": "true1234",
            }
        )
        self.assertEqual(form.errors["email"], ["User with this Email already exists."])

    def test_username_too_short(self):
        form = UserCreationForm(
            data={
                "username": "Te",
                "email": "testuser1310@mail.com",
                "password1": "true1234",
                "password2": "true1234",
            }
        )
        self.assertEqual(
            form.errors["username"],
            ["Ensure this value has at least 3 characters (it has 2)."],
        )

    def test_username_too_long(self):
        form = UserCreationForm(
            data={
                "username": "123456789-123456789-123456789-1",
                "email": "testuser1310@mail.com",
                "password1": "true1234",
                "password2": "true1234",
            }
        )
        self.assertEqual(
            form.errors["username"],
            ["Ensure this value has at most 30 characters (it has 31)."],
        )

    def test_email_too_short(self):
        form = UserCreationForm(
            data={
                "username": "TestUser123",
                "email": "t@d.d",
                "password1": "true1234",
                "password2": "true1234",
            }
        )
        self.assertEqual(
            form.errors["email"],
            ["Enter a valid email address."],
        )

    def test_email_too_long(self):
        form = UserCreationForm(
            data={
                "username": "TestUser123",
                "email": "testuser1310testuser1310@mailmailmailmailabcdef.com",
                "password1": "true1234",
                "password2": "true1234",
            }
        )
        self.assertEqual(
            form.errors["email"],
            ["Ensure this value has at most 50 characters (it has 51)."],
        )


class EmailAndUsernameChangeFormTest(CreateTestInstances, TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="TestUser11015",
            email="testuser11015@mail.com",
        )
        self.user.set_password("testpw99")
        self.user.save()

    def test_valid_form_username(self):
        form = EmailAndUsernameChangeForm(
            instance=self.user,
            data={
                "username": "TestUser1090",
            },
        )
        form.is_valid()
        self.assertTrue(form.is_valid())

    def test_valid_form_email(self):
        form = EmailAndUsernameChangeForm(
            instance=self.user,
            data={
                "email": "testUser1090@mail.com",
            },
        )
        self.assertTrue(form.is_valid())

    def test_username_already_exists(self):
        form = EmailAndUsernameChangeForm(
            instance=self.user,
            data={
                "username": "TestUser1",
            },
        )
        self.assertEqual(form.errors["username"], ["Username is already in use."])

    def test_email_already_exists(self):
        form = EmailAndUsernameChangeForm(
            instance=self.user,
            data={
                "email": "testuser1@mail.com",
            },
        )
        self.assertEqual(form.errors["email"], ["Email is already in use."])

    def test_username_too_short(self):
        form = EmailAndUsernameChangeForm(
            instance=self.user,
            data={
                "username": "Te",
            },
        )
        self.assertEqual(
            form.errors["username"],
            ["Ensure this value has at least 3 characters (it has 2)."],
        )

    def test_username_too_long(self):
        form = EmailAndUsernameChangeForm(
            instance=self.user,
            data={
                "username": "123456789-123456789-123456789-1",
            },
        )
        self.assertEqual(
            form.errors["username"],
            ["Ensure this value has at most 30 characters (it has 31)."],
        )

    def test_email_too_short(self):
        form = EmailAndUsernameChangeForm(
            instance=self.user,
            data={
                "email": "t@d.d",
            },
        )
        self.assertEqual(
            form.errors["email"],
            ["Enter a valid email address."],
        )

    def test_email_too_long(self):
        form = EmailAndUsernameChangeForm(
            instance=self.user,
            data={
                "email": "testuser1310testuser1310@mailmailmailmailabcdef.com",
            },
        )
        self.assertEqual(
            form.errors["email"],
            ["Ensure this value has at most 50 characters (it has 51)."],
        )


class PasswordChangingFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="TestUser1101",
            email="testuser1101@mail.com",
        )
        self.user.set_password("testpw99")
        self.user.save()

    def test_valid_form(self):
        form = PasswordChangingForm(
            user=self.user,
            data={
                "old_password": "testpw99",
                "new_password1": "true1234",
                "new_password2": "true1234",
            },
        )
        self.assertTrue(form.is_valid())

    def test_no_old_password(self):
        form = PasswordChangingForm(
            user=self.user,
            data={
                "new_password1": "true1234",
                "new_password2": "true1234",
            },
        )
        self.assertFalse(form.is_valid())

    def test_new_password_too_short(self):
        form = PasswordChangingForm(
            user=self.user,
            data={
                "old_password": "testpw99",
                "new_password1": "true123",
                "new_password2": "true123",
            },
        )
        self.assertEqual(
            form.errors["new_password2"],
            ["This password is too short. It must contain at least 8 characters."],
        )

    def test_wrong_second_password(self):
        form = PasswordChangingForm(
            user=self.user,
            data={
                "new_password1": "true1234",
                "new_password2": "wrong1234",
            },
        )
        self.assertEqual(
            form.errors["new_password2"], ["The two password fields didn’t match."]
        )


class TimezoneChangeFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="TestUser1100", email="testuser1100@mail.com"
        )

    def test_form_valid_timezone(self):
        """Test that form accepts valid timezones"""
        form = TimezoneChangeForm(
            instance=self.user.profile, data={"timezone": "Europe/London"}
        )
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(self.user.profile.timezone, "Europe/London")

    def test_form_invalid_timezone(self):
        """Test that form rejects invalid timezones"""
        form = TimezoneChangeForm(
            instance=self.user.profile, data={"timezone": "Invalid/Timezone"}
        )
        self.assertFalse(form.is_valid())

    def test_form_blank_timezone(self):
        """Test that form requires timezone field"""
        form = TimezoneChangeForm(instance=self.user.profile, data={})
        self.assertFalse(form.is_valid())
