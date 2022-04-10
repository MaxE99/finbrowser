# Django imports
from django import forms
from django.forms import ModelForm
# Local imports
from home.models import List


class AddListForm(ModelForm):

    class Meta:
        model = List
        fields = ['name', 'content_type', 'sources']
        widgets = {'sources': forms.CheckboxSelectMultiple}
