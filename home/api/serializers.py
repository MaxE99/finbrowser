# Django imports
from rest_framework import serializers
# Local imports
from home.models import (Source, List, Article, HighlightedArticle, SourceRating, ListRating)
from accounts.models import Profile, SocialLink


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


class Profile_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = '__all__'


class HighlightedArticle_Serializer(serializers.ModelSerializer):

    class Meta:
        model = HighlightedArticle
        fields = '__all__'


class SocialLink_Serializer(serializers.ModelSerializer):

    class Meta:
        model = SocialLink
        fields = '__all__'

class SourceRating_Serializer(serializers.ModelSerializer):

    class Meta:
        model = SourceRating
        fields = '__all__'

class ListRating_Serializer(serializers.ModelSerializer):

    class Meta:
        model = ListRating
        fields = '__all__'