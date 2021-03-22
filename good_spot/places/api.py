from constance import config
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models import Count, When, Case, CharField, Value, Q, F
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from rest_framework import mixins, viewsets, status, generics
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from django_filters import rest_framework as filters
from structlog import get_logger

from good_spot.filter import models as filter_models
from good_spot.places import models as places_models
from good_spot.places.openapidoc import documentation
from good_spot.places import serializers as places_serializers
from good_spot.places import filters as places_filters
from good_spot.populartimes.fill_place_data import identify_city
from good_spot.common.tasks import send_email_async

log = get_logger()


class PlaceViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   documentation.PlaceViewSetJsonSchema,
                   viewsets.GenericViewSet):
    '''
    Returns list of published places which have `location`.\n
    Provide `city` in params to filter places by city.\n
    Expected the name of city in `city` params.
    '''
    serializer_class = places_serializers.PlaceModelSerializer
    short_serializer_class = places_serializers.ShortPlaceModelSerializer
    retrieve_serializer_class = places_serializers.PlaceRetrieveModelSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.retrieve_serializer_class
        return self.serializer_class

    def get_queryset(self):
        queryset = places_models.Place.objects.filter(
            is_published=True, location__isnull=False
        ).prefetch_related(
            'place_types'
        )
        filter_city_id = self.request.query_params.get('city_id', None)
        filter_type_id = self.request.query_params.get('type_id', None)
        if filter_city_id:
            try:
                city = places_models.City.objects.get(id=filter_city_id)
                queryset = queryset.filter(city=city)
            except places_models.City.DoesNotExist:
                return queryset.none()
        else:
            # TODO remove temporary solution
            filter_city = self.request.query_params.get('city', None)
            if filter_city:
                city_qs = places_models.City.objects.filter(name=filter_city)
                if city_qs:
                    queryset = queryset.filter(city=city_qs.first())

        if filter_type_id:
            queryset = queryset.filter(place_types__id=filter_type_id)

        return queryset.prefetch_related(
            'actualpopulartimes'
        ).prefetch_related(
            'place_images'
        )

    @detail_route(methods=["get"])
    def short_description(self, request, *args, **kwargs):
        '''
        Expected only param `id`
        '''
        # return short description and features
        obj = self.get_object()
        data = self.short_serializer_class(instance=obj).data
        return Response(data)


class FilterViewSet(documentation.FilterViewSetJsonSchema,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    '''
    Provide GET parameter 'city_id' to get filter corresponding to chosen city
    '''
    queryset = places_models.PlaceType.objects.filter(is_active=True, slug__isnull=False)
    serializer_class = places_serializers.PlaceTypeSerializer
    allowed_methods = ['get', 'post']
    filter_serializer_class = places_serializers.FilterPlaceSerializer
    place_serializer_class = places_serializers.PlaceModelSerializer

    def get_queryset(self):
        queryset = self.queryset
        filter_city_id = self.request.query_params.get('city_id', None)

        if filter_city_id:
            queryset = queryset.filter(
                Q(active_in_cities=filter_city_id) &
                Q(place__city_id=filter_city_id)
            ).distinct()

        # TODO remove temporary solution with city=<str>
        if not filter_city_id:
            filter_city = self.request.query_params.get('city', None)
            if filter_city:
                city_qs = places_models.City.objects.filter(name=filter_city)
                if city_qs:
                    queryset = queryset.filter(
                        active_in_cities=city_qs.first().id,
                        place__city_id=city_qs.first().id
                    ).distinct()

        return queryset.order_by('id')

    # this method named `create` instead of `post` to make post documentation visible in Swagger api docs.
    # BTW nothing creates here.
    def create(self, request, *args, **kwargs):
        # TODO remove temporary solution
        data = request.data
        if not data.get('city_id') and data.get('city'):
            city_qs = places_models.City.objects.filter(name=data['city'])
            if city_qs:
                data['city_id'] = city_qs.first().id

        serializer = self.filter_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        filters = serializer.data.get('filter')
        price = serializer.data.get('price')
        slug = serializer.data.get('slug')
        city_id = serializer.data.get('city_id')

        places_queryset = places_models.Place.objects.prefetch_related('place_types').filter(
            is_published=True,
            city_id=city_id,
            place_types__slug=slug,
            location__isnull=False
        )

        if price:
            places_queryset = places_queryset.filter(google_price_level__in=price)

        for filter in filters:
            if filter.get('field_type') == 'bool':
                if filter.get('data'):
                    # v1
                    places_subquery = filter_models.PlaceBoolFilterField.objects.filter(
                        value=filter.get('data'),
                        field_type__id=filter.get('id')
                    ).values_list('place__id', flat=True)
                else:
                    # v2
                    places_subquery = filter_models.PlaceBoolFilterField.objects.filter(
                        value=filter.get('options'),
                        field_type__id=filter.get('id')
                    ).values_list('place__id', flat=True)
                places_queryset = places_queryset.filter(id__in=places_subquery)
            elif filter.get('field_type') == 'choice':
                if filter.get('data'):
                    # v1
                    places_subquery = filter_models.PlaceChoiceFilterField.objects.filter(
                        value__option=filter.get('data'),
                        field_type__id=filter.get('id')
                    ).values_list('place__id', flat=True)
                else:
                    # v2
                    places_subquery = filter_models.PlaceChoiceFilterField.objects.filter(
                        value__id=filter.get('options'),
                        field_type__id=filter.get('id')
                    ).values_list('place__id', flat=True)

                places_queryset = places_queryset.filter(id__in=places_subquery)
            elif filter.get('field_type') == 'multi':
                if filter.get('data'):
                    # v1
                    places_subquery = filter_models.PlaceChoiceFilterField.objects.filter(
                        value__option__in=filter.get('data'),
                        field_type__id=filter.get('id')
                    ).values_list('place__id', flat=True)
                else:
                    # v2
                    places_subquery = filter_models.PlaceChoiceFilterField.objects.filter(
                        value__id__in=filter.get('options'),
                        field_type__id=filter.get('id')
                    ).values_list('place__id', flat=True)

                places_queryset = places_queryset.filter(id__in=places_subquery)

        filtered_places_serializer = self.place_serializer_class(instance=places_queryset, many=True,
                                                                 context={
                                                                     "request": request,
                                                                     "type_id": 2
                                                                 })
        return Response(filtered_places_serializer.data, status=status.HTTP_200_OK)


class PlaceTypeViewSet(
    documentation.PlaceTypeViewSetJsonSchema,
    viewsets.GenericViewSet,
    mixins.ListModelMixin):
    '''
    Returns the list of all place types.\n
    Object contains param `is_default`.\n
    `is_default` defines that tab with filters of this place type should be opened by default.\n
    If all are false, open the first.
    '''
    serializer_class = places_serializers.PlaceTypeListSerializer
    allowed_methods = ['get']
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = places_filters.PlaceTypeFilter

    def get_queryset(self):
        queryset = places_models.PlaceType.objects.filter(
            is_active=True,
            slug__isnull=False
        ).annotate(
            places_count=Count('place')
        ).filter(
            places_count__gt=0
        )
        filter_city_id = self.request.query_params.get('city_id', None)
        if filter_city_id:
            queryset = queryset.filter(place__city_id=filter_city_id).distinct()
        return queryset


class CityListAPIView(documentation.CityListAPIViewJsonSchema, ListAPIView):
    '''
    Returns the list of all active cities that should be displayed in dropdown menu.
    If there are no places in city it shouldn't be displayed.
    '''
    serializer_class = places_serializers.AvailableCitySerializer
    query_params_serializer_class = places_serializers.LatLngSerializer

    def get_queryset(self):
        qs = places_models.City.objects.filter(is_active=True).select_related('city')

        if not qs.count():
            return []

        # Return list of cities if city contains places.
        qs = qs.annotate(
            places_count=Count('place')
        ).filter(
            places_count__gt=0
        ).order_by('city__country__name', 'city__name')

        if not qs.count():
            return []

        query_params_serializer = self.query_params_serializer_class(data=self.request.query_params)
        query_params_serializer.is_valid(raise_exception=True)

        if self.request.query_params.get('lat', None) and self.request.query_params.get('lng', None):
            lat = float(self.request.query_params['lat'])
            lng = float(self.request.query_params['lng'])
            closest = identify_city(lat, lng)

            if closest:
                # It means that user is in the city 
                return qs.annotate(
                    current_city=Case(
                        When(id=closest.id, then=Value("native")),
                        default=None,
                        output_field=CharField()
                    )
                )
            else:
                # it means that user is in the absent city and we return closest city
                p = Point(lng, lat, srid=4326)
                closest = qs.annotate(distance=Distance('point', p)).order_by('distance').first()
        else:
            try:
                default_city = places_models.City.objects.get(is_default=True)
                closest = default_city
            except places_models.City.DoesNotExist:
                closest = qs.first()

        return qs.annotate(
            current_city=Case(
                When(id=closest.id, then=Value("closest")),
                default=None,
                output_field=CharField()
            )
        )


class SearchListAPIView(documentation.SearchListAPIViewJsonSchema,
                        generics.ListAPIView):
    serializer_class = places_serializers.SearchSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = places_filters.PlaceFilter

    def get_queryset(self):
        queryset = places_models.Place.place_types.through.objects.filter(
            placetype__active_in_cities=F('place__city'),
            place__city__is_active=True,
            placetype__is_active=True,
            place__is_published=True,
            place__location__isnull=False
        ).select_related(
            'place', 'placetype', 'place__city'
        ).order_by(
            'place__name', 'placetype__name'
        )

        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(
                Q(place__name__unaccent__istartswith=name) | Q(place__name__unaccent__icontains=name)
            )
        return queryset


class FrequentationUpdateAPIView(generics.CreateAPIView):
    queryset = places_models.Frequentation.objects.all()
    serializer_class = places_serializers.FrequentationSerializer
    permission_classes = (IsAuthenticated,)


class PlaceReportAPIView(generics.RetrieveAPIView,
                         generics.CreateAPIView):
    queryset = places_models.Place.objects.filter(is_published=True, location__isnull=False)
    serializer_class = places_serializers.PlaceReportSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            log.msg("Reported data from user for place is valid.")
            subject = _("User's report about place.")
            body_html = render_to_string('emails/place_report.html', {
                'place_data': request.data
            }, request=request)
            log.msg("Tries to run celery task to send email.")
            # send_email_async.delay(
            #     subject,
            #     body_html,
            #     config.CONTACT_EMAIL
            # )
            emails = [config.CONTACT_EMAIL] if config.CONTACT_EMAIL else list(settings.ADMINS)
            msg = EmailMessage(
                subject,
                body_html,
                settings.DEFAULT_FROM_EMAIL,
                emails,
            )
            msg.content_subtype = 'html'
            msg.send(fail_silently=True)

            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
