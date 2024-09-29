from typing import Any, Dict

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm, ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from apps.accounts.models import Profile

User = get_user_model()


class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required fields,
    plus a repeated password field for confirmation.
    """

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Enter Password"}),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"}),
    )

    class Meta:
        model = User
        fields = ("username", "email")
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Username"}),
            "email": forms.TextInput(attrs={"placeholder": "Email"}),
        }

    def clean_password2(self) -> str:
        """
        Validate that the two password fields match.

        Returns:
            str: The confirmed password if it matches password1.

        Raises:
            ValidationError: If the two passwords don't match.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit: bool = True):
        """
        Save the user instance with a hashed password.

        Args:
            commit (bool): Whether to save the user instance immediately.

        Returns:
            User: The created user instance.

        Raises:
            ValidationError: If there's an error during user creation.
        """
        try:
            user = super().save(commit=False)
            user.set_password(self.cleaned_data["password1"])
            if commit:
                user.save()
            return user
        except Exception as error:
            raise ValidationError(f"User creation failed due to: {error}")


class UserChangeForm(forms.ModelForm):
    """
    A form for updating existing users in the admin interface.

    This form includes all user fields, but the password field is replaced
    with a read-only display of the hashed password, which cannot be changed
    directly through this form. This form is intended for admin use only,
    allowing administrators to update user details like username and email.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ("username", "email", "password")


class EmailAndUsernameChangeForm(forms.ModelForm):
    """
    A form for updating the username and email of a user.

    This form pre-populates the username and email fields with values passed
    via kwargs and includes validation to ensure that the username and email
    are unique across the user base, excluding the current user.
    """

    def __init__(self, *args: Any, **kwargs: Dict[str, Any]) -> None:
        """
        Initializes the form with the provided username and email.

        Args:
            args: Positional arguments passed to the parent class.
            kwargs: Keyword arguments including `username` and `email`.
        """

        self.username = kwargs.pop("username", None)
        self.email = kwargs.pop("email", None)
        super().__init__(*args, **kwargs)

        self.fields["username"].widget = forms.TextInput(
            attrs={
                "value": self.username,
                "minlength": 3,
                "maxlength": 30,
            }
        )
        self.fields["email"].widget = forms.TextInput(
            attrs={
                "value": self.email,
                "minlength": 5,
                "maxlength": 50,
            }
        )

    class Meta:
        model = User
        fields = ("username", "email")
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Username"}),
            "email": forms.TextInput(attrs={"placeholder": "Email"}),
        }

    def clean_username(self) -> str:
        """
        Validates that the provided username is unique, excluding the current user.

        Returns:
            str: The cleaned username if it is unique.

        Raises:
            forms.ValidationError: If the username is already in use by another user.
        """
        username = self.cleaned_data.get("username")
        if (
            username
            and User.objects.exclude(pk=self.instance.pk)
            .filter(username=username)
            .exists()
        ):
            raise forms.ValidationError("Username is already in use.")
        return username

    def clean_email(self) -> str:
        """
        Validates that the provided email is unique, excluding the current user.

        Returns:
            str: The cleaned email if it is unique.

        Raises:
            forms.ValidationError: If the email is already in use by another user.
        """
        email = self.cleaned_data.get("email", None)
        if (
            email
            and User.objects.exclude(pk=self.instance.pk).filter(email=email).exists()
        ):
            raise forms.ValidationError("Email is already in use.")
        return email


class PasswordChangingForm(PasswordChangeForm):
    """
    A form for changing a user's password, extending Django's PasswordChangeForm.

    This form includes three fields: old password, new password, and confirmation of the new password.
    It uses password input widgets to mask the entered characters.
    """

    old_password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={
                "type": "password",
                "label": "Old password",
            }
        ),
    )
    new_password1 = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(attrs={"type": "password", "label": "New password"}),
    )
    new_password2 = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(
            attrs={"type": "password", "label": "Confirm new password"}
        ),
    )

    class Meta:
        model = User
        fields = ("old_password", "new_password1", "new_password2")

    def __init__(self, *args: Any, **kwargs: Dict[str, Any]) -> None:
        """
        Initializes the PasswordChangingForm with the given arguments.

        Args:
            args: Positional arguments passed to the parent class.
            kwargs: Keyword arguments passed to the parent class.
        """
        super(PasswordChangingForm, self).__init__(*args, **kwargs)
        self.fields["new_password1"].label = "New password"
        self.fields["new_password2"].label = "Confirm new password"


class TimezoneChangeForm(forms.ModelForm):
    """
    A form for changing a user's timezone in their profile.

    This form pre-populates the timezone field with an optional value passed via kwargs.
    """

    class Meta:
        model = Profile
        fields = ("timezone",)
        labels = {"timezone": "Timezone"}

    def __init__(self, *args: Any, **kwargs: Dict[str, Any]) -> None:
        """
        Initializes the TimezoneChangeForm with an optional timezone value.

        Args:
            args: Positional arguments passed to the parent class.
            kwargs: Keyword arguments, must include 'timezone' for pre-population.
        """
        self.timezone = kwargs.pop("timezone", None)
        super(TimezoneChangeForm, self).__init__(*args, **kwargs)
        self.fields["timezone"].initial = self.timezone
