from rest_framework import mixins, viewsets

from good_spot.places import models as places_models
from good_spot.place_editor import serializers as place_editor_serializer
from good_spot.populartimes.fill_place_data import fill_place


class PlaceEditorViewSet(mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):
    queryset = places_models.Place.objects.all()
    serializer_class = place_editor_serializer.PlaceEditorSaveSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        fill_place(instance.google_place_id)
