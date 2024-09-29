from django.forms import ModelForm

from apps.support.models import Contact


class ContactForm(ModelForm):
    """
    A form for submitting contact information.

    This form is tied to the `Contact` model and includes all fields defined in that model.
    """

    class Meta:
        model = Contact
        fields = "__all__"
