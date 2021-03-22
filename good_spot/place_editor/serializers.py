import json

from rest_framework import serializers
from good_spot.places import models as places_models
from good_spot.filter import models as filter_models
from good_spot.places.tasks import fill_place_async, update_frequentation_async


class PlaceInitSchemaSerializer(serializers.ModelSerializer):
    # Uses for `startval` in schema

    class Meta:
        model = places_models.Place
        fields = ('__all__')

    def to_representation(self, instance):
        ret = super(PlaceInitSchemaSerializer, self).to_representation(instance)
        res = {}

        available_choice_filters = filter_models.ChoiceFilterField.objects.filter(
            place_type__in=instance.place_types.all())
        for obj in available_choice_filters:
            res[obj.id] = []
        available_bool_filters = filter_models.BoolFilterField.objects.filter(place_type__in=instance.place_types.all())
        for obj in available_bool_filters:
            res[obj.id] = False
        available_text_filters = filter_models.TextFilterField.objects.filter(place_type__in=instance.place_types.all())
        for obj in available_text_filters:
            res[obj.id] = ""

        for obj in filter_models.PlaceChoiceFilterField.objects.filter(place=instance):
            res[obj.field_type_id] = list(obj.value.values_list('id', flat=True))
        for obj in filter_models.PlaceBoolFilterField.objects.filter(place=instance):
            res[obj.field_type_id] = obj.value

        for obj in filter_models.TextFilterField.objects.filter(place_type__in=instance.place_types.all()):
            try:
                translated_object = filter_models.PlaceTextFilterField.objects.get(place=instance, field_type=obj)
                res[obj.id] = {
                    "{}_en".format(obj.id): translated_object.value_en,
                    "{}_fr".format(obj.id): translated_object.value_fr,
                    "{}_ru".format(obj.id): translated_object.value_ru,
                    "{}_uk".format(obj.id): translated_object.value_uk
                }
            except filter_models.PlaceTextFilterField.DoesNotExist:
                res[obj.id] = {
                    "{}_en".format(obj.id): '',
                    "{}_fr".format(obj.id): '',
                    "{}_ru".format(obj.id): '',
                    "{}_uk".format(obj.id): ''
                }

        ret['place_filters'] = res

        return ret


class PlaceEditorSaveSerializer(serializers.ModelSerializer):
    place_filters = serializers.JSONField(required=False)
    populartimes = serializers.JSONField(required=False)

    class Meta:
        model = places_models.Place
        fields = ('__all__')

    def validate_populartimes(self, value):
        if value and isinstance(value, str):
            value = json.loads(value)
        else:
            value = None
        return value

    def validate_open_hours(self, value):
        if value and isinstance(value, str):
            value = json.loads(value)
        else:
            value = None
        return value

    def validate_google_data(self, value):
        if value and isinstance(value, str):
            value = json.loads(value)
        else:
            value = None
        return value

    def validate_extended_place_types(self, value):
        if value and isinstance(value, str):
            value = json.loads(value)
        else:
            value = None
        return value

    def create(self, validated_data):
        instance = super(PlaceEditorSaveSerializer, self).create(validated_data)
        fill_place_async.delay(instance.google_place_id)
        update_frequentation_async.delay(instance.google_place_id)
        return instance

    def update(self, instance, validated_data):

        # TODO make it more flexible
        for fld in validated_data:
            if isinstance(fld, str) and fld.endswith(('_en', '_fr', '_ru', '_uk')) and validated_data[fld] == '':
                validated_data[fld] = None

        instance = super(PlaceEditorSaveSerializer, self).update(instance, validated_data)
        if validated_data.get('place_types'):
            place_types_data = validated_data.pop('place_types')
            place_types_exists = list(instance.place_types.all())

            place_types_add = list(set(place_types_data) - set(place_types_exists))
            instance.place_types.add(*place_types_add)

            place_types_remove = list(set(place_types_exists) - set(place_types_data))
            instance.place_types.remove(*place_types_remove)

        place_filters_data = validated_data.get("place_filters")
        place_filters = []
        for key, value in place_filters_data.items():
            filter_field = filter_models.FilterField.objects.get(id=key)
            if filter_field.id in instance.place_filter_field.values_list('field_type__id', flat=True):
                if isinstance(filter_field, filter_models.ChoiceFilterField):
                    place_filter_field = filter_models.PlaceChoiceFilterField.objects.get(
                        place=instance,
                        field_type=filter_field
                    )
                    choices_exists = list(place_filter_field.value.values_list('id', flat=True))
                    choices_add = list(set(value) - set(choices_exists))
                    choices_remove = list(set(choices_exists) - set(value))
                    place_filter_field.value.add(*choices_add)
                    place_filter_field.value.remove(*choices_remove)
                elif isinstance(filter_field, filter_models.BoolFilterField):
                    filter_models.PlaceBoolFilterField.objects.filter(
                        place=instance,
                        field_type=filter_field
                    ).update(value=value)
                elif isinstance(filter_field, filter_models.TextFilterField):
                    # TODO manage languages dynamically
                    filter_models.PlaceTextFilterField.objects.filter(
                        place=instance,
                        field_type=filter_field
                    ).update(
                        value_en=value.get('{}_en'.format(filter_field.id)),
                        value_fr=value.get('{}_fr'.format(filter_field.id)),
                        value_ru=value.get('{}_ru'.format(filter_field.id)),
                        value_uk=value.get('{}_uk'.format(filter_field.id))
                    )
            else:
                if isinstance(filter_field, filter_models.ChoiceFilterField):
                    place_filter_field = filter_models.PlaceChoiceFilterField.objects.create(
                        place=instance,
                        field_type=filter_field
                    )
                    choices_exists = list(place_filter_field.value.values_list('id', flat=True))
                    choices_add = list(set(value) - set(choices_exists))
                    choices_remove = list(set(choices_exists) - set(value))
                    place_filter_field.value.add(*choices_add)
                    place_filter_field.value.remove(*choices_remove)
                elif isinstance(filter_field, filter_models.BoolFilterField):
                    filter_models.PlaceBoolFilterField.objects.create(
                        place=instance,
                        field_type=filter_field,
                        value=value
                    )
                elif isinstance(filter_field, filter_models.TextFilterField):
                    # TODO manage languages dynamically
                    filter_models.PlaceTextFilterField.objects.create(
                        place=instance,
                        field_type=filter_field,
                        value_en=value.get('{}_en'.format(filter_field.id)),
                        value_fr=value.get('{}_fr'.format(filter_field.id)),
                        value_ru=value.get('{}_ru'.format(filter_field.id)),
                        value_uk=value.get('{}_uk'.format(filter_field.id))
                    )

            place_filters.append({
                "id": key,
                "value": value
            })

        return instance
