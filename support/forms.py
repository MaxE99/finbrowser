# Django imports
from django.forms import ModelForm
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


class BugReportForm(ModelForm):

    class Meta:
        model = BugReport
        fields = ('url', 'type', 'explanation')
