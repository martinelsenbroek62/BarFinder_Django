from django.db.models import Case, When, BooleanField
from django.utils.translation import ugettext as _
from rest_framework import serializers

from good_spot.filter import models as filter_models
from good_spot.users import models as users_models
from good_spot.places.models import City


class PlaceChoiceFilterFieldSerializer(serializers.ModelSerializer):
    is_selected = serializers.SerializerMethodField()

    class Meta:
        model = filter_models.ChoiceFilterFieldOption
        fields = ('id', 'option', 'is_selected')

    def get_is_selected(self, obj):
        return obj.is_selected if hasattr(obj, 'is_selected') else None


class FilterFieldModelSerializer(serializers.ModelSerializer):
    data = serializers.SerializerMethodField('get_options')
    options = serializers.SerializerMethodField('get_options_with_id')
    field_type = serializers.SerializerMethodField()
    places_count = serializers.SerializerMethodField()

    class Meta:
        model = filter_models.FilterField
        fields = ('id', 'name', 'data', 'options', 'field_type', 'is_shown_in_short_description', 'places_count')

    def get_places_count(self, obj):
        return obj.place_filter_field.all().distinct().count()

    def get_options(self, obj):
        query_param_city_id = self.context['request'].query_params.get("city_id", None)
        try:
            place_type = self.context['place_type']
        except:
            raise serializers.ValidationError({
                'options': _('Expected `place_type` in context but it was not received.')
            })

        if isinstance(obj, filter_models.ChoiceFilterField):
            option_pks = []
            # TODO remove temporary solution with city=<str>
            if not query_param_city_id:
                filter_city = self.context['request'].query_params.get('city', None)
                if filter_city:
                    city_qs = City.objects.filter(name=filter_city)
                    if city_qs:
                        option_pks = filter_models.PlaceChoiceFilterField.objects.filter(
                            place__city_id=city_qs.first().id,
                            place__place_types=place_type
                        ).exclude(value=None).values_list('value__id', flat=True)
            else:
                option_pks = filter_models.PlaceChoiceFilterField.objects.filter(
                    place__city_id=query_param_city_id,
                    place__place_types=place_type
                ).exclude(value=None).values_list('value__id', flat=True)

            res = obj.choice_options.filter(id__in=option_pks).values_list("option", flat=True)

            return res

        return None

    def get_options_with_id(self, obj):
        query_param_city_id = self.context['request'].query_params.get("city_id", None)
        place_type = self.context['place_type']

        if isinstance(obj, filter_models.ChoiceFilterField):
            option_pks = []
            # TODO remove temporary solution with city=<str>
            if not query_param_city_id:
                filter_city = self.context['request'].query_params.get('city', None)
                if filter_city:
                    city_qs = City.objects.filter(name=filter_city)
                    if city_qs:
                        option_pks = filter_models.PlaceChoiceFilterField.objects.filter(
                            place__city_id=city_qs.first().id,
                            place__place_types=place_type
                        ).exclude(value=None).values_list('value__id', flat=True)
            else:
                option_pks = filter_models.PlaceChoiceFilterField.objects.filter(
                    place__city_id=query_param_city_id,
                    place__place_types=place_type
                ).exclude(value=None).values_list('value__id', flat=True)

            res = PlaceChoiceFilterFieldSerializer(
                instance=obj.choice_options.filter(id__in=option_pks), many=True
            ).data

            return res

        return None

    def get_field_type(self, obj):
        if isinstance(obj, filter_models.BoolFilterField):
            return 'bool'
        elif isinstance(obj, filter_models.TextFilterField):
            return 'text'
        elif isinstance(obj, filter_models.ChoiceFilterField) and not obj.is_multi:
            return 'choice'
        elif isinstance(obj, filter_models.ChoiceFilterField) and obj.is_multi:
            return 'multi'


class UserFilterFieldModelSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField('get_options_with_id')

    class Meta:
        model = filter_models.FilterField
        fields = ('id', 'name', 'options')

    def get_options_with_id(self, obj):
        users_options = []
        if self.context.get('user', None):
            user = self.context['user']
            users_options = users_models.FavoriteChoiceFilterField.objects.filter(
                user=user,
                filter_field=obj
            ).values_list('value', flat=True)

        selected_options = obj.choice_options.annotate(
            is_selected=Case(
                When(
                    id__in=list(users_options), then=True
                ),
                default=False,
                output_field=BooleanField()
            )
        )

        return PlaceChoiceFilterFieldSerializer(
            instance=selected_options, many=True
        ).data


class PlaceFilterFieldSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField('get_options_with_id')
    data = serializers.SerializerMethodField('get_value')
    name = serializers.SerializerMethodField()
    filter_field_type = serializers.SerializerMethodField()

    class Meta:
        model = filter_models.PlaceFilterField
        fields = ('id', 'name', 'field_type', 'data', 'options', 'filter_field_type')

    def get_name(self, obj):
        return obj.field_type.name

    def get_value(self, obj):
        if isinstance(obj, filter_models.PlaceBoolFilterField):
            return obj.value
        return None

    def get_filter_field_type(self, obj):
        if isinstance(obj, filter_models.PlaceBoolFilterField):
            return 'bool'
        elif isinstance(obj, filter_models.PlaceTextFilterField):
            return 'text'
        elif isinstance(obj, filter_models.PlaceChoiceFilterField):
            return 'choice'

    def get_options_with_id(self, obj):

        if isinstance(obj, filter_models.PlaceChoiceFilterField):
            selected_values = obj.value.values_list('pk', flat=True)

            all_options = obj.field_type.choice_options.annotate(
                is_selected=Case(
                    When(
                        id__in=list(selected_values),
                        then=True
                    ),
                    default=False,
                    output_field=BooleanField()
                )
            )

            return PlaceChoiceFilterFieldSerializer(
                instance=all_options, many=True
            ).data

        return None


class ReportFilterFieldSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField('get_options_with_id')
    data = serializers.SerializerMethodField('get_value')
    filter_field_type = serializers.SerializerMethodField()

    class Meta:
        model = filter_models.FilterField
        fields = ('id', 'name', 'data', 'options', 'filter_field_type')

    def get_value(self, obj):
        place = self.context['place']

        if isinstance(obj, filter_models.BoolFilterField):
            try:
                return filter_models.PlaceBoolFilterField.objects.get(field_type=obj, place=place).value
            except filter_models.PlaceBoolFilterField.DoesNotExist:
                return False
        return None

    def get_options_with_id(self, obj):
        place = self.context['place']

        if isinstance(obj, filter_models.ChoiceFilterField):
            place_options = []

            if filter_models.PlaceChoiceFilterField.objects.filter(field_type=obj, place=place):
                place_options = filter_models.PlaceChoiceFilterField.objects.get(
                    field_type=obj, place=place
                ).value.values_list(
                    'pk', flat=True
                )

            selected_options = obj.choice_options.annotate(
                is_selected=Case(
                    When(
                        id__in=list(place_options), then=True
                    ),
                    default=False,
                    output_field=BooleanField()
                )
            )

            return PlaceChoiceFilterFieldSerializer(
                instance=selected_options, many=True
            ).data

        return None

    def get_filter_field_type(self, obj):
        if isinstance(obj, filter_models.BoolFilterField):
            return 'bool'
        elif isinstance(obj, filter_models.TextFilterField):
            return 'text'
        elif isinstance(obj, filter_models.ChoiceFilterField):
            return 'choice'
