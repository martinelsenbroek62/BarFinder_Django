import jwt
from django.conf import settings
from rest_framework import serializers

from good_spot.images.models import PlaceImage


class PlaceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceImage
        fields = ('__all__')


class NotifierSerializer(serializers.Serializer):
    payload = serializers.CharField()

    def validate(self, attrs):
        payload = attrs.get('payload')
        try:
            payload = jwt.decode(payload, settings.NOTIFIER_SECRET, algorithms=['HS256'])

            filename = payload['filename']
            PlaceImage.objects.filter(
                image='images/{}'.format(filename)
            ).update(
                thumbnail='resized-images/{}'.format(filename)
            )
        except Exception as e:
            raise serializers.ValidationError(e)
        return {
            'success': True
        }
