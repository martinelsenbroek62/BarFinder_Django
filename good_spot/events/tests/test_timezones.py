from django.test import TestCase
from datetime import datetime
from django.utils import timezone
from cities_light import models as citieslight_models
from good_spot.places import models as places_models
from good_spot.places import factories as places_factories
from good_spot.places import tasks as places_tasks
from good_spot.events import models as events_models
from good_spot.events import factories as events_factories


class CityTimezoneTestCase(TestCase):
    fixtures = [
        'good_spot/fixtures/test_timezones/citieslight_countries.json',
        'good_spot/fixtures/test_timezones/citieslight_cities.json',
        'good_spot/fixtures/test_timezones/application_cities.json',
        'good_spot/fixtures/test_timezones/placetype_active_in_cities.json',
    ]

    def test_fixtures(self):
        assert citieslight_models.Country.objects.count() == 3
        assert citieslight_models.City.objects.count() == 3
        assert places_models.City.objects.count() == 3
        assert places_models.PlaceType.objects.count() == 4
        assert places_models.PlaceType.objects.get(pk=1).active_in_cities.count() == 3

    def setUp(self):
        for i in range(5):
            places_factories.PlaceFactory(city=places_models.City.objects.get(pk=1))
        assert places_models.Place.objects.count() == 5

        for i in range(3):
            places_factories.PlaceFactory(city=places_models.City.objects.get(pk=2))
        assert places_models.Place.objects.count() == 8

        for i in range(2):
            places_factories.PlaceFactory(city=places_models.City.objects.get(pk=3))
        assert places_models.Place.objects.count() == 10

        place_type = places_models.PlaceType.objects.get(slug='bar')
        for place in places_models.Place.objects.all():
            place.place_types.add(place_type)

        rule_time = timezone.utc.localize(datetime(
            year=2018,
            month=1,
            day=1,
            hour=18,
            minute=0
        ))
        rule = events_factories.UpdatingRuleFactory(
            start=rule_time,
            rule="DAILY"
        )
        assert events_models.UpdatingRule.objects.count() == 1

        rule_relation = events_models.UpdatingRuleRelation(
            rule=rule,
            content_object=place_type
        )
        rule_relation.save()
        assert events_models.UpdatingRuleRelation.objects.count() == 1

    def test_timezones(self):
        current_server_time = timezone.now().replace(hour=15, minute=0, second=0, microsecond=0)
        count_of_updated_places = places_tasks._process_timezones(current_server_time)
        assert count_of_updated_places == 2

        current_server_time = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
        count_of_updated_places = places_tasks._process_timezones(current_server_time)
        assert count_of_updated_places == 5

        current_server_time = timezone.now().replace(hour=23, minute=0, second=0, microsecond=0)
        count_of_updated_places = places_tasks._process_timezones(current_server_time)
        assert count_of_updated_places == 3
