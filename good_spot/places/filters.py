from django_filters import rest_framework as filters
from django_filters import CharFilter
from good_spot.places import models as places_models


class PlaceFilter(filters.FilterSet):
    city_id = CharFilter(name='place__city__id')

    class Meta:
        model = places_models.Place.place_types.through
        fields = ['city_id', ]


class PlaceTypeFilter(filters.FilterSet):
    class Meta:
        model = places_models.PlaceType
        fields = ['active_in_cities']
