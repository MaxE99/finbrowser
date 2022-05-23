# Django imports
from django.forms import ModelForm
from django import forms
# Python imports
from datetime import date
# Local imports
from home.models import List, Sector


class AddListForm(ModelForm):

    class Meta:
        model = List
        fields = ['name', 'list_pic', 'is_public']
        labels = {'list_pic': 'Picture', 'is_public': 'Make playlist public'}
    

class ListNameChangeForm(ModelForm):

    class Meta:
        model = List
        fields = ('name', )


class ListPicChangeForm(ModelForm):

    class Meta:
        model = List
        fields = ('list_pic', )


class AddExternalArticleForm(forms.Form):
    website_name = forms.CharField(max_length=100, label="Website Url")
    sector = forms.ModelChoiceField(queryset=Sector.objects.all())
    title = forms.CharField(max_length=100)
    link = forms.URLField()
    pub_date = forms.DateField(label="Publication Date",
                               widget=forms.DateInput(attrs=dict(type='date')))

    def clean_pub_date(self):
        pub_date = self.cleaned_data['pub_date']
        if pub_date > date.today() or pub_date < date(1990, 1, 1):
            raise forms.ValidationError('This date is wrong!')
        return pub_date