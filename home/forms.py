# Django imports
from django.forms import ModelForm
# Local imports
from home.models import List, ExternalArticle


class AddListForm(ModelForm):

    class Meta:
        model = List
        fields = ['name', 'list_pic', 'content_type', 'is_public']
        labels = {'list_pic': 'Picture', 'is_public': 'Make playlist public'}


class ListNameChangeForm(ModelForm):

    class Meta:
        model = List
        fields = ('name', )


class ListPicChangeForm(ModelForm):

    class Meta:
        model = List
        fields = ('list_pic', )


class AddExternalArticlesForm(ModelForm):

    class Meta:
        model = ExternalArticle
        fields = ('title', 'link', 'sector', 'pub_date')
