from rest_framework import serializers
from good_spot.pages import models as pages_models


class PageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = pages_models.Page
        fields = ('id', 'title', 'short_description', 'text')
