import googlemaps
import reverse_geocoder as rg
from cities_light.models import Country
from django.conf import settings
from django.contrib.gis.geos import Point
from django.db.models import Q, Count
from django.utils import timezone
from googlemaps.exceptions import ApiError
from structlog import get_logger

from good_spot.places.models import Place, City, PlaceType, Frequentation
from good_spot.populartimes.crawler import get_current_popular_times
from good_spot.populartimes.exceptions import WrongResponseException
from good_spot.populartimes.models import Populartimes
from good_spot.proxy.exceptions import IPOverUsageException

log = get_logger()


def identify_city(lat: float, lng: float):
    if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
        raise TypeError("Latitude and longitude have to be an integer type or a float type.")

    results = rg.search((lat, lng))

    for result in results:
        city_name = result["name"]
        try:
            cities_qs = City.objects.filter(
                is_active=True
            ).annotate(
                places_count=Count('place')
            ).filter(
                places_count__gt=0
            )
            city = cities_qs.get(city__name=city_name)
            return city
        except City.DoesNotExist:
            log.error('City `{}` is absent. lat={}, lng={}'.format(city_name, lat, lng))
            return None


def fill_place(place_id):
    log.msg("Filling place with place_id={} started.".format(place_id))
    gmaps = googlemaps.Client(key=settings.GOOGLE_PLACES_API_KEY)

    try:
        gmaps_response = gmaps.place(place_id, language='en')
    except ApiError as e:
        log.error("Place_id={} can't be handled.".format(place_id))
        return

    if gmaps_response.get('status', None) and gmaps_response['status'] == 'OK':
        gmaps_place_response = gmaps_response['result']

        place_obj, place_obj_created = Place.objects.get_or_create(google_place_id=place_id)

        if not place_obj.block_city:
            search_country_name = [
                x['long_name'] for x in gmaps_place_response['address_components'] if 'country' in x['types']
            ]
            if not search_country_name:
                log.error("It's not possible to detect country for place with place_id={}".format(place_id))
                return
            country_name = search_country_name[0]
            country = None
            try:
                country = Country.objects.get(name=country_name)
            except Country.DoesNotExist:
                log.error("Provided country is not available.")

            search_city_name = [
                x['long_name'] for x in gmaps_place_response['address_components'] if 'locality' in x['types']
            ]
            if not search_city_name:
                log.error("It's not possible to detect city for place with place_id={}".format(place_id))
                return
            city_name = search_city_name[0]
            city = None
            try:
                city = City.objects.get(
                    Q(city__name=city_name) | Q(name_variants__contains=city_name),
                    city__country=country
                )
            except City.DoesNotExist:
                log.error("Provided city is not available.")
            place_obj.city = city

        if not place_obj.block_name:
            place_obj.name = gmaps_place_response.get('name', None)
        if not place_obj.block_google_rating:
            place_obj.google_rating = gmaps_place_response.get('rating', None)
        if not place_obj.block_google_price_level:
            place_obj.google_price_level = gmaps_place_response.get('price_level', None)
        if gmaps_place_response.get('geometry', None) and not place_obj.block_location:
            location = gmaps_place_response['geometry'].get('location', None)
            place_obj.location = Point(location['lng'], location['lat'])
        if not place_obj.block_address:
            place_obj.address = gmaps_place_response.get('formatted_address', None)
        if not place_obj.block_website:
            place_obj.website = gmaps_place_response.get('website', None)
        if not place_obj.block_phone:
            place_obj.phone = gmaps_place_response.get('international_phone_number', None)
        place_obj.open_hours = gmaps_place_response.get('opening_hours', None)
        place_obj.google_data = gmaps_place_response

        place_obj.save()

        if not place_obj.block_place_types:
            place_types = [
                place_type for place_type in PlaceType.objects.all() if place_type.slug in gmaps_place_response['types']
            ]
            place_obj.place_types.clear()
            place_obj.place_types.add(*place_types)


def update_frequentation(place_id):
    log.msg("Updating frequentation for place_id={} started.".format(place_id))
    try:
        place_obj = Place.objects.get(google_place_id=place_id)

        try:
            log.msg("`get_current_popular_times` started.")
            popular_times = get_current_popular_times(place_id)
            log.msg("`get_current_popular_times` ended.")

            if popular_times.get('populartimes', None):
                place_obj.populartimes = popular_times['populartimes']
                place_obj.save()

                # Save like a history to be able to analise data
                Populartimes.objects.create(
                    place=place_obj,
                    populartimes=popular_times['populartimes']
                )

            if popular_times.get('current_popularity', None):
                frequentation = Frequentation.objects.create(
                    place=place_obj,
                    value=popular_times['current_popularity']
                )
                place_obj.actualize_popular_time(frequentation=frequentation)

            if popular_times.get('extended_place_types', None):
                place_obj.extended_place_types = popular_times['extended_place_types']

            place_obj.populartimes_updated_at = timezone.now()
            place_obj.save()
        except WrongResponseException:
            log.error("Process stopped because of wrong response from Google API.")
        except IPOverUsageException:
            log.error("Process stopped for place_id={} because of external IPs over usage.".format(place_id))
        except Exception as e:
            log.error(str(e))
            log.error(
                "Something went wrong when try to get popular times for place with place_id={}".format(place_id))

    except Place.DoesNotExist:
        log.warning("Place with place_id={} doesn't exist.".format(place_id))
