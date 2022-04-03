# Django imports
from rest_framework import serializers
# Local imports
from home.models import Source, List, Article


class Source_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Source
        fields = '__all__'


class Article_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = '__all__'


class List_Serializer(serializers.ModelSerializer):

    class Meta:
        model = List
        fields = '__all__'