import factory
import random

from good_spot.places import models as places_models


def random_city():
    city_count = places_models.City.objects.count()
    return places_models.City.objects.all()[random.randrange(1, city_count)]


class PlaceFactory(factory.DjangoModelFactory):
    class Meta:
        model = places_models.Place

    google_place_id = factory.Sequence(lambda n: 'google_place_id_%s' % n)
    city = factory.LazyFunction(random_city)


class CityFactory(factory.DjangoModelFactory):
    class Meta:
        model = places_models.City
