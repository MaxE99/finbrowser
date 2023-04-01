# Django imports
from django.forms import ModelForm

# Local imports
from apps.support.models import Contact


class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = "__all__"
