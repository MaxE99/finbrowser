from django import forms
from allauth.account.forms import SignupForm


class CustomSignUpForm(SignupForm):
    """
    Custom signup form that extends the default SignupForm to include
    an additional field for terms and privacy agreement.
    """

    terms_and_privacy = forms.BooleanField(required=True)
    field_order = ["username", "email", "password1", "password2", "terms_and_privacy"]
