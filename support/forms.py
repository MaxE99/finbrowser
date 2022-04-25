# Django imports
from django.forms import ModelForm
from django import forms
# Local imports
from support.models import SourceSuggestion, BugReport, FeatureSuggestion


class SourceSuggestionForm(ModelForm):

    class Meta:
        model = SourceSuggestion
        fields = ('url', 'sector')


class FeatureSuggestionForm(ModelForm):

    class Meta:
        model = FeatureSuggestion
        fields = ('website_part', 'suggestion', 'explanation')
        labels = {
            'website_part': 'Where in website should this new feature be?:',
            'suggestion': 'Type of feature:',
            'explanation': 'Explanation of the feature:'
        }
        widgets = {
            'explanation':
            forms.Textarea(attrs={
                'rows': 10,
                'cols': 22,
                'style': 'resize:none;'
            }),
        }


class BugReportForm(ModelForm):

    class Meta:
        model = BugReport
        fields = ('url', 'type', 'explanation')
        labels = {
            'url': 'URL where bug occured:',
            'type': 'Type of bug:',
            'explanation': 'Explanation of the bug:'
        }
        widgets = {
            'explanation':
            forms.Textarea(attrs={
                'rows': 10,
                'cols': 22,
                'style': 'resize:none;'
            }),
        }
