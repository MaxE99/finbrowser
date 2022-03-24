# Django imports
from rest_framework import serializers
# Local imports
from home.models import BrowserSource


class Source_Serializer(serializers.ModelSerializer):

    class Meta:
        model = BrowserSource
        fields = '__all__'