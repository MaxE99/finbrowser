# Django imports
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
from django.template.defaultfilters import slugify
# Local imports
from apps.accounts.models import Profile
from apps.base_logger import logger

User = get_user_model()

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'}))
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email'}),
        }

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        try:
            user = super().save(commit=False)
            user.set_password(self.cleaned_data["password1"])
            if commit:
                user.save()
            return user
        except:
            logger.exception('User save method failed!')


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class EmailAndUsernameChangeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', None)
        self.email = kwargs.pop('email', None)
        super(EmailAndUsernameChangeForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = forms.TextInput(
            attrs={'value': self.username})
        self.fields['email'].widget = forms.TextInput(
            attrs={'value': self.email})

    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Username',
            }),
            'email': forms.TextInput(attrs={'placeholder': 'Email'}),
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists() or User.objects.exclude(pk=self.instance.pk).filter(profile__slug=slugify(username)).exists():
            raise forms.ValidationError('Username is already in use.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('Email is already in use.')
        return email


class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(attrs={
            'type': 'password',
            'label': 'Old password',
        }))
    new_password1 = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(attrs={
            'type': 'password',
            'label': 'New password'
        }))
    new_password2 = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(attrs={
            'type': 'password',
            'label': 'Confirm new password'
        }))

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')

    def __init__(self, *args, **kwargs):
        super(PasswordChangingForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].label = "New password"
        self.fields['new_password2'].label = "Confirm new password"


class ProfilePicChangeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('profile_pic',)
        labels = {
            'profile_pic': 'Profile Picture'
        }

class TimezoneChangeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.timezone = kwargs.pop('timezone', None)
        super(TimezoneChangeForm, self).__init__(*args, **kwargs)
        self.fields['timezone'].initial = self.timezone

    class Meta:
        model = Profile
        fields = ('timezone',)
        labels = {
            'timezone': 'Timezone'
        }
