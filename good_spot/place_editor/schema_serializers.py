from collections import OrderedDict

from rest_framework import serializers
from rest_framework import fields as rf_fields
from rest_framework import relations as rf_relations

from good_spot.places import models as places_models
from good_spot.filter import models as filter_models


class SchemaMixin(object):
    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = self._readable_fields

        def process_field(pfield, order):
            params = {}
            params.update({
                'headerTemplate': pfield.label,
                'propertyOrder': order
            })
            # if pfield.help_text:
            #     params.update({
            #         'description': pfield.help_text
            #     })

            if isinstance(pfield, rf_fields.IntegerField) or isinstance(pfield, rf_fields.FloatField):
                params.update({
                    'type': 'number'
                })
            elif isinstance(pfield, rf_fields.BooleanField):
                params.update({
                    'type': 'boolean',
                    'format': 'checkbox'
                })
            elif isinstance(pfield, rf_relations.PrimaryKeyRelatedField):
                qs = pfield.get_queryset()
                params.update({
                    'type': 'number',
                    'enum': list(qs.values_list('id', flat=True)),
                    'options': {
                        'enum_titles': list(qs.values_list('name', flat=True))
                    }
                })
            elif isinstance(pfield, rf_relations.ManyRelatedField):
                qs = pfield.child_relation.get_queryset()
                params.update({
                    'type': 'array',
                    'uniqueItems': 'true',
                    'items': {
                        'type': 'number',
                        'enum': list(qs.values_list('id', flat=True)),
                        'options': {
                            'enum_titles': list(qs.values_list('name', flat=True))
                        }
                    }
                })
            elif isinstance(pfield, rf_fields.JSONField):
                params.update({
                    'type': 'string',
                    'format': 'json'
                })
            else:
                params.update({
                    'type': 'string'
                })
            return params

        order = 0
        for field in fields:
            ret[field.field_name] = process_field(field, order)
            order += 1

        return ret


class PlaceGenerateEditSchema(SchemaMixin, serializers.ModelSerializer):
    # Uses for generate schema for edit place
    class Meta:
        model = places_models.Place
        fields = ['google_place_id',
                  'is_published',
                  'city',
                  'block_city',
                  'name_en',
                  'name_fr',
                  'name_ru',
                  'name_uk',
                  'block_name',
                  'place_types',
                  'block_place_types',
                  'google_rating',
                  'block_google_rating',
                  'google_price_level',
                  'block_google_price_level',
                  'location',
                  'block_location',
                  'address_en',
                  'address_fr',
                  'address_ru',
                  'address_uk',
                  'block_address',
                  'website',
                  'block_website',
                  'phone',
                  'block_phone',
                  'open_hours',
                  'google_data',
                  'long_description',
                  'special_event_en',
                  'special_event_fr',
                  'special_event_ru',
                  'special_event_uk',
                  'is_gay_friendly',
                  'update_populartimes',
                  'populartimes'
                  ]

    def to_representation(self, instance):
        ret = super(PlaceGenerateEditSchema, self).to_representation(instance)

        field_properties = {}
        order = 0

        available_choice_filters = filter_models.ChoiceFilterField.objects.filter(
            place_type__in=instance.place_types.all())
        for choice_field in available_choice_filters:
            field_properties.update({
                choice_field.id: {
                    "type": "array",
                    "uniqueItems": "true",
                    "propertyOrder": order,
                    "title": choice_field.name,
                    "format": "checkbox",
                    "items": {
                        "type": "integer",
                        "enum": list(choice_field.choice_options.values_list('id', flat=True)),
                        "options": {
                            "enum_titles": list(choice_field.choice_options.values_list('option', flat=True))
                        }
                    }
                }
            })
            order += 1

        available_bool_filters = filter_models.BoolFilterField.objects.filter(place_type__in=instance.place_types.all())
        for bool_field in available_bool_filters:
            field_properties.update({
                bool_field.id: {
                    "type": "boolean",
                    "format": "checkbox",
                    "propertyOrder": order,
                    "title": bool_field.name
                }
            })
            order += 1

        available_text_filters = filter_models.TextFilterField.objects.filter(place_type__in=instance.place_types.all())
        for text_field in available_text_filters:
            field_properties.update({
                text_field.id: {
                    "type": "string",
                    "propertyOrder": order,
                    "title": text_field.name
                }
            })
            order += 1

            # TODO manage languages dynamically
            field_properties[text_field.id] = {
                "type": "object",
                "propertyOrder": order,
                "format": "grid",
                "grid_columns": 4,
                "title": text_field.name,
                "properties": {
                    "{}_en".format(text_field.id): {
                        "type": "string",
                        "title": "{} [en]".format(text_field.name),
                        "propertyOrder": 1,
                    },
                    "{}_fr".format(text_field.id): {
                        "type": "string",
                        "title": "{} [fr]".format(text_field.name),
                        "propertyOrder": 2,
                    },
                    "{}_ru".format(text_field.id): {
                        "type": "string",
                        "title": "{} [ru]".format(text_field.name),
                        "propertyOrder": 3,
                    },
                    "{}_uk".format(text_field.id): {
                        "type": "string",
                        "title": "{} [uk]".format(text_field.name),
                        "propertyOrder": 4,
                    }
                }
            }

        ret['place_filters'] = {
            "type": "object",
            "title": "Place fields",
            "format": "table",
            "properties": field_properties
        }

        return ret
