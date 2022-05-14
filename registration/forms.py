# Django imports
from django import forms
from allauth.account.forms import SignupForm

class CustomSignUpForm(SignupForm):
    terms_and_privacy = forms.BooleanField(required=True)
    field_order = ['username', 'email', 'password1', 'password2', 'terms_and_privacy']