# Django imports
from django import forms
# Local imports
from datetime import date

class AddExternalArticleForm(forms.Form):
    website_name = forms.CharField(max_length=100, label="Website Url")
    title = forms.CharField(max_length=100)
    link = forms.URLField()
    pub_date = forms.DateField(label="Publication Date",
                               widget=forms.DateInput(attrs=dict(type='date')))

    def clean_pub_date(self):
        pub_date = self.cleaned_data['pub_date']
        if pub_date > date.today() or pub_date < date(1990, 1, 1):
            raise forms.ValidationError('This date is wrong!')
        return pub_date