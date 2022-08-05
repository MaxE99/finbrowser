# Django imports
from django import forms
# Local imports
from apps.home.models import Notification

class KeywordNotificationCreationForm(forms.ModelForm):

    class Meta:
        model = Notification
        fields = ('keyword', )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(KeywordNotificationCreationForm, self).__init__(*args, **kwargs)

    def clean_keyword(self):
        keyword = self.cleaned_data['keyword']
        if Notification.objects.exclude(pk=self.instance.pk).filter(user=self.request.user, keyword=keyword).exists():
            raise forms.ValidationError('You have already created a keyword with this term!')
        return keyword
    
    def save(self, commit=True):
        instance = super(KeywordNotificationCreationForm, self).save(commit=False)
        instance.user = self.request.user
        if commit:
            instance.save()
        return instance