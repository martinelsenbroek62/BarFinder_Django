import random
from django.contrib.gis.geos import Point
from mixer.backend.django import Mixer
from rest_framework import status, serializers
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from faker import Faker

from good_spot.places.models import Place, PlaceType

fake = Faker()
mixer = Mixer(commit=False)
mocked_objects_count = 10
place_rating_choice = list(range(1, 5))

place_types = []

place_type_choice = ["bar", "restaurant", "night club"]
pl_i = 1
for pl_type in place_type_choice:
    place_type = mixer.blend(PlaceType)
    place_type.id = pl_i
    place_type.name = pl_type
    place_types.append(place_type)
    pl_i += 1


def make_place(place_id):
    place = mixer.blend(Place)
    place.id = place_id
    place.name = fake.name()
    place.google_rating = fake.random_element(place_rating_choice)
    random_point = Point(
        random.uniform(50.4, 50.5),
        random.uniform(30.44, 30.62)
    )
    place.location = random_point
    place.google_data = {}
    place.populartimes = {}
    return place


class PlaceTypeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceType
        fields = ('id', 'name')


class PlaceModelSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = ('id', 'name', 'google_place_id', 'place_types', 'google_rating', 'location',
                  'populartimes')

    def get_location(self, obj):
        return {
            'lat': obj.location.y,
            'lng': obj.location.x
        }

    def to_representation(self, instance):
        ret = super(PlaceModelSerializer, self).to_representation(instance)

        place_type_response = PlaceTypeModelSerializer(instance=place_types, many=True).data
        ret.update({
            'place_types': [fake.random_element(place_type_response)]
        })
        return ret


class PlaceRetrieveModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ('id', 'name', 'google_place_id', 'place_types', 'google_rating', 'location', 'address', 'website',
                  'phone', 'long_description', 'open_hours', 'populartimes')

    def to_representation(self, instance):
        ret = super(PlaceRetrieveModelSerializer, self).to_representation(instance)

        place_type_response = PlaceTypeModelSerializer(instance=place_types, many=True).data
        ret.update({
            'place_types': [fake.random_element(place_type_response)]
        })
        return ret


class PlaceMockAPIView(APIView):

    def get(self, request):
        place_serializer = PlaceModelSerializer(instance=Place.objects.all(), many=True)

        return Response(status=status.HTTP_200_OK, data=place_serializer.data)


class PlaceMockRetrieveAPIView(RetrieveAPIView):
    def retrieve(self, request, *args, **kwargs):
        place = make_place(kwargs['pk'])
        place_serializer = PlaceRetrieveModelSerializer(instance=place)
        return Response(status=status.HTTP_200_OK, data=place_serializer.data)
