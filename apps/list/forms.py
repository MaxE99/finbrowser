# Django imports
from django.forms import ModelForm
# Local imports
from apps.list.models import List


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
