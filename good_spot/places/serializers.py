import copy
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from rest_framework import serializers
from structlog import get_logger

from good_spot.filter import models as filter_models
from good_spot.filter import serializers as filter_serializers
from good_spot.images.serializers import PlaceImageSerializer
from good_spot.places import models as places_models

log = get_logger()


class PlaceTypeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = places_models.PlaceType
        fields = ('id', 'name', 'slug', 'is_default')


class PlaceTypeAnnotatedSerializer(serializers.ModelSerializer):
    is_selected = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = places_models.PlaceType
        fields = ('id', 'name', 'slug', 'is_default', 'is_selected')

    def get_is_selected(self, obj):
        return obj.is_selected

    def get_name(self, obj):
        return obj.name_plural or obj.name


class PlaceModelSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    place_types = PlaceTypeModelSerializer(many=True)
    populartimes = serializers.SerializerMethodField('get_actual_populartimes')
    place_images_count = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()

    class Meta:
        model = places_models.Place
        fields = ('id',
                  'name',
                  'preview',
                  'place_images_count',
                  'features',
                  'short_description',
                  'google_place_id',
                  'place_types',
                  'google_rating',
                  'google_price_level',
                  'location',
                  'is_gay_friendly',
                  'populartimes'
                  )

    def get_actual_populartimes(self, obj):
        return obj.actualpopulartimes.value if hasattr(obj, 'actualpopulartimes') else obj.populartimes

    def get_location(self, obj):
        return {
            'lat': obj.location.y,
            'lng': obj.location.x
        }

    def get_place_images_count(self, obj):
        return obj.place_images.count()

    def get_short_description(self, obj):
        if not obj.short_description:
            return None

        query_param_type_id = self.context['request'].query_params.get("type_id", None) or self.context.get('type_id')
        if not query_param_type_id:
            return None

        place_type = places_models.PlaceType.objects.filter(id=query_param_type_id).first()

        if place_type and obj.short_description.get(place_type.slug, None):
            return obj.short_description[place_type.slug]
        else:
            str_list = list(obj.short_description.values())
            str_list = list(filter(None, str_list))
            return ', '.join([v for v in str_list])


class PlaceRetrieveModelSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()
    about_place = serializers.SerializerMethodField()
    place_types = PlaceTypeModelSerializer(many=True)
    place_fields = serializers.SerializerMethodField()
    place_fields_keys = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    populartimes = serializers.SerializerMethodField('get_actual_populartimes')
    place_images = serializers.SerializerMethodField()
    place_images_count = serializers.SerializerMethodField()

    class Meta:
        model = places_models.Place
        fields = ('id', 'name', 'features', 'short_description', 'about_place', 'google_place_id', 'is_gay_friendly',
                  'place_types', 'google_rating', 'google_price_level', 'location', 'address', 'website',
                  'phone', 'long_description', 'special_event', 'place_fields', 'place_fields_keys', 'open_hours',
                  'populartimes', 'place_images_count', 'place_images')

    def get_actual_populartimes(self, obj):
        return obj.actualpopulartimes.value if hasattr(obj, 'actualpopulartimes') else obj.populartimes

    def get_location(self, obj):
        return {
            'lat': obj.location.y,
            'lng': obj.location.x
        }

    def get_short_description(self, obj):
        # TODO replace using `place_type` by `type_id` as we do in PlaceModelSerializer
        if not obj.get_grouped_short_description():
            return None
        query_param_place_type = self.context['request'].query_params.get("place_type", None)

        if query_param_place_type and not obj.get_grouped_short_description().get(query_param_place_type, None):
            return None
        elif query_param_place_type and obj.get_grouped_short_description().get(query_param_place_type, None):
            return obj.get_grouped_short_description()[query_param_place_type]
        else:
            str_list = list(obj.get_grouped_short_description().values())
            str_list = list(filter(None, str_list))
            return ', '.join([v for v in str_list])

    def get_about_place(self, obj):
        query_param_place_type = self.context['request'].query_params.get("place_type", None)
        place_fields = obj.place_filter_field.filter(field_type__is_shown_in_about_place=True).order_by(
            'field_type__order')
        if query_param_place_type:
            place_fields = place_fields.filter(field_type__place_type__slug=query_param_place_type)
        res = []
        for pf in place_fields:
            if isinstance(pf, filter_models.PlaceChoiceFilterField):
                res += list(pf.value.values_list('option', flat=True))
            elif isinstance(pf, filter_models.PlaceBoolFilterField) and pf.value:
                res.append(pf.field_type.name)
            elif isinstance(pf, filter_models.PlaceTextFilterField) and pf.value:
                res.append(pf.value)

        return res

    def get_features(self, obj):
        query_param_place_type = self.context['request'].query_params.get("place_type", None)
        if not obj.get_grouped_features():
            return None

        if query_param_place_type and not obj.get_grouped_features().get(query_param_place_type, None):
            return None
        if query_param_place_type and obj.get_grouped_features().get(query_param_place_type, None):
            return obj.get_grouped_features()[query_param_place_type]
        else:
            res = []
            for val in obj.get_grouped_features().values():
                res += val
            return res

    def get_place_fields(self, obj):
        query_param_place_type = self.context['request'].query_params.get("place_type", None)
        place_fields = obj.place_filter_field.all().order_by("field_type__order")
        if query_param_place_type:
            place_fields = place_fields.filter(field_type__place_type__slug=query_param_place_type). \
                order_by("field_type__order")
        res = {}

        for pf in place_fields:
            if isinstance(pf, filter_models.PlaceBoolFilterField):
                if pf.value:
                    res.update(
                        {pf.field_type.name: ""}
                    )
            elif isinstance(pf, filter_models.PlaceChoiceFilterField):
                res_list = list(pf.value.values_list("option", flat=True))
                if res_list:
                    res.update(
                        {pf.field_type.name: ", ".join(res_list)}
                    )
            elif isinstance(pf, filter_models.PlaceTextFilterField):
                if pf.value:
                    res.update(
                        {pf.field_type.name: pf.value}
                    )
        return res

    def get_place_fields_keys(self, obj):
        return [*self.get_place_fields(obj)]

    def get_place_images(self, obj):
        return PlaceImageSerializer(instance=obj.place_images.all()[:4], many=True).data

    def get_place_images_count(self, obj):
        return obj.place_images.count()


class PlaceTypeSerializer(serializers.ModelSerializer):
    filters = serializers.SerializerMethodField('get_field_types')
    price = serializers.SerializerMethodField()

    class Meta:
        model = places_models.PlaceType
        fields = ('id', 'name', 'slug', 'price', 'filters')

    def get_price(self, obj):
        return list(range(1, 5))

    def get_active_place_count(self, obj):
        return places_models.Place.objects.filter(place_types=obj).count()

    def get_field_types(self, obj):
        # import pdb;pdb.set_trace()
        items = filter_models.FilterField.objects.filter(place_type=obj, is_public=True, is_filter=True)

        query_param_city_id = self.context['request'].query_params.get("city_id", None)
        if query_param_city_id:
            items = items.filter(
                place_filter_field__place__city_id=query_param_city_id,
                place_filter_field__place__place_types=obj
            ).distinct()

        # TODO remove temporary solution with city=<str>
        if not query_param_city_id:
            filter_city = self.context['request'].query_params.get('city', None)
            if filter_city:
                city_qs = places_models.City.objects.filter(name=filter_city)
                if city_qs:
                    items = items.filter(
                        place_filter_field__place__city_id=city_qs.first().id,
                        place_filter_field__place__place_types=obj
                    ).distinct()

        context = self.context
        context['place_type'] = obj
        serializer = filter_serializers.FilterFieldModelSerializer(instance=items, many=True, context=context)

        # quick solution to remove filter fields with empty options list
        serializer_data = copy.deepcopy(serializer.data)
        for i, item in enumerate(serializer_data):
            if item['options'] == []:
                del serializer_data[i]

        return serializer_data


class FilterPlaceSerializer(serializers.Serializer):
    city_id = serializers.IntegerField()
    filter = serializers.JSONField()
    slug = serializers.CharField()
    price = serializers.ListField(required=False, child=serializers.IntegerField(min_value=1, max_value=4))

    def validate_city(self, city_id):
        if not places_models.City.objects.filter(city_id=city_id).exists():
            raise serializers.ValidationError(_('City does not exist.'))
        return city_id

    def validate_slug(self, slug):
        if not places_models.PlaceType.objects.filter(slug=slug).exists():
            raise serializers.ValidationError(_('Incorrect slug.'))
        return slug

    def validate_filter(self, filter):
        updated_filter = []
        for attr in filter:
            field_type_id = attr.get('id', None)
            field_type_data = attr.get('data', None)
            field_type_options = attr.get('options', None)

            if not field_type_id:
                raise serializers.ValidationError(_('Please, provide `id` for every filter\'s attribute.'))
            if not field_type_data and not field_type_options:
                raise serializers.ValidationError(_('Please, provide `data` or `options` '
                                                    'for every filter\'s attribute.'))
            try:
                field_type_obj = filter_models.FilterField.objects.get(id=field_type_id)
                if isinstance(field_type_obj, filter_models.ChoiceFilterField) \
                        and field_type_obj.is_multi:
                    if field_type_data and not isinstance(field_type_data, list):
                        raise serializers.ValidationError(_('data for filter with id={} should be list, not {}.'
                                                            .format(field_type_id, type(field_type_data))))
                    if field_type_options and not isinstance(field_type_options, list):
                        raise serializers.ValidationError(_('options for filter with id={} should be list, not {}.'
                                                            .format(field_type_id, type(field_type_options))))
                if isinstance(field_type_obj, filter_models.ChoiceFilterField):
                    attr['field_type'] = 'multi' if field_type_obj.is_multi else 'choice'
                elif isinstance(field_type_obj, filter_models.BoolFilterField):
                    attr['field_type'] = 'bool'
                elif isinstance(field_type_obj, filter_models.TextFilterField):
                    attr['field_type'] = 'text'
                else:
                    raise serializers.ValidationError(_('Unexpected type ob object {}'.format(field_type_obj)))
                updated_filter.append(attr)
            except filter_models.FilterField.DoesNotExist:
                raise serializers.ValidationError(_('FieldType object with provided id={} does not exist.'
                                                    .format(field_type_id)))
        return updated_filter


class PlaceTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = places_models.PlaceType
        fields = ('id', 'slug', 'name', 'is_default')


class AvailableCitySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    current_city = serializers.SerializerMethodField()

    class Meta:
        model = places_models.City
        fields = ('id', 'name', 'country', 'timezone', 'latitude', 'longitude', 'name_variants', 'current_city',
                  'is_default')

    def get_name(self, obj):
        return obj.name

    def get_country(self, obj):
        return obj.country_name

    def get_latitude(self, obj):
        return obj.city.latitude

    def get_longitude(self, obj):
        return obj.city.longitude

    def get_current_city(self, obj):
        # it is annotated field
        return obj.current_city


class LatLngSerializer(serializers.Serializer):
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)


class SearchPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = places_models.Place
        fields = ['id', 'name', 'city']


class SearchPlaceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = places_models.PlaceType
        fields = ['id', 'name', 'slug']


class SearchSerializer(serializers.ModelSerializer):
    place = PlaceRetrieveModelSerializer()
    place_type = serializers.SerializerMethodField()

    class Meta:
        model = places_models.Place.place_types.through
        fields = ['id', 'place', 'place_type']

    def get_place_type(self, obj):
        return SearchPlaceTypeSerializer(instance=obj.placetype).data


class CitySerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()

    class Meta:
        model = places_models.City
        fields = ['id', 'name', 'country']

    def get_country(self, obj):
        return obj.country.name


class FrequentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = places_models.Frequentation
        fields = ['id', 'place', 'value']

    def create(self, validated_data):
        try:
            user = self.context['request'].user
        except Exception:
            raise serializers.ValidationError(
                {
                    'user': 'Expected user in request.'
                }
            )

        if not user.is_authenticated():
            raise serializers.ValidationError(
                {
                    'user': 'Expected authorized user.'
                }
            )

        validated_data.update({
            'user': user,
            'is_hidden': True,
            'origin_from_user': True
        })

        return super(FrequentationSerializer, self).create(validated_data)


class PlaceReportSerializer(serializers.ModelSerializer):
    place_filter_field = serializers.SerializerMethodField()

    class Meta:
        model = places_models.Place
        fields = ['id', 'name', 'google_price_level', 'place_filter_field']

    def get_place_filter_field(self, obj):
        place_type = self.context.get('request').query_params.get('place_type')

        if not place_type:
            raise serializers.ValidationError({
                'place_filter_field': _('Expected `place_type` in query params but it was not received.')
            })

        try:
            int(place_type)
        except ValueError:
            raise serializers.ValidationError({
                'place_filter_field': _('Expected `place_type` is integer but it is {}.'.format(type(place_type)))
            })

        text_ct = ContentType.objects.get_for_model(filter_models.TextFilterField)
        qs = filter_models.FilterField.objects.filter(
            place_type=place_type
        ).exclude(
            polymorphic_ctype=text_ct
        )

        context = self.context
        context['place'] = obj
        return filter_serializers.ReportFilterFieldSerializer(instance=qs, many=True, context=context).data


class ShortPlaceModelSerializer(serializers.ModelSerializer):
    short_description = serializers.SerializerMethodField('get_live_short_description')
    features = serializers.SerializerMethodField('get_live_features')
    place_types = PlaceTypeModelSerializer(many=True)

    class Meta:
        model = places_models.Place
        fields = ['id',
                  'name',
                  'preview',
                  'place_types',
                  'google_place_id',
                  'short_description',
                  'features',
                  'google_rating',
                  'is_gay_friendly']

    def get_live_short_description(self, obj):
        return obj.get_grouped_short_description()

    def get_live_features(self, obj):
        return obj.get_grouped_features()
