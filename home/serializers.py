# Django imports
from rest_framework import serializers
# Local imports
from home.models import BrowserSource, List


class Source_Serializer(serializers.ModelSerializer):

    class Meta:
        model = BrowserSource
        fields = '__all__'


class List_Serializer(serializers.ModelSerializer):

    class Meta:
        model = List
        fields = '__all__'