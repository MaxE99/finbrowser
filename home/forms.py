# Django imports
from django import forms
from django.forms import ModelForm
# Local imports
from home.models import BrowserSource


class AddSourceForm(ModelForm):

    class Meta:
        model = BrowserSource
        fields = ['source', 'category']


# class SearchSettingsForm(forms.Form):
#     SEARCH_TIMEFRAME_CHOICES = [
#         ('All', 'All'),
#         ('Last 24 Hours', 'Last 24 Hours'),
#         ('Last 7 Days', 'Last 7 Days'),
#         ('Last 30 Days', 'Last 30 Days'),
#         ('Last 365 Days', 'Last 365 Days'),
#     ]
#     sources = forms.ModelMultipleChoiceField(
#         queryset=BrowserSource.objects.all().order_by('domain'),
#         initial=[option for option in BrowserSource.objects.all()],
#         widget=forms.CheckboxSelectMultiple)
#     timeframe = forms.ChoiceField(choices=SEARCH_TIMEFRAME_CHOICES)
#     search_term = forms.CharField(
#         required=False,
#         max_length=120,
#         widget=forms.TextInput(
#             attrs={'placeholder': 'Enter specific search term'}))
