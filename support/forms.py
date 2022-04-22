# Django imports
from django.forms import ModelForm
# Local imports
from support.models import SourceSuggestion


class SourceSuggestionForm(ModelForm):

    class Meta:
        model = SourceSuggestion
        fields = ('url', 'sector')