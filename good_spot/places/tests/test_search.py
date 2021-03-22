import json

from django.contrib.gis.geos import Point
from test_plus import APITestCase
from good_spot.places import models as places_models
from cities_light import models as citieslight_model
from good_spot.places import factories


class CityListAPIViewTestCase(APITestCase):
    fixtures = [
        'good_spot/fixtures/countries.json',
        'good_spot/fixtures/cities.json',
    ]

    def setUp(self):
        for cl in citieslight_model.City.objects.all():
            places_models.City.objects.create(
                city=cl
            )

        self.place1 = factories.PlaceFactory(name='Sky Bar')
        self.place2 = factories.PlaceFactory(name='Wine Bar')
        self.place3 = factories.PlaceFactory(name='Lounge Bar', location=Point(1, 1))

    def test_get_empty(self):
        response = self.get('api:places:search')
        self.response_200()

        data = json.loads(response.content)
        self.assertEqual(data, [])

    def test_get(self):
        place_type = places_models.PlaceType.objects.first()
        place_type.active_in_cities.add(self.place3.city)
        place_type.is_active = True
        place_type.save()
        self.place3.place_types.add(place_type)
        self.place3.save()

        response = self.get('api:places:search')
        self.response_200()
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)

        self.place1.location = Point(1, 1)
        self.place1.place_types.add(places_models.PlaceType.objects.first())
        self.place1.save()

        self.place2.location = Point(1, 1)
        self.place2.place_types.add(places_models.PlaceType.objects.first())
        self.place2.save()

        response = self.get('api:places:search')
        self.response_200()
        data = json.loads(response.content)
        self.assertEqual(len(data), places_models.Place.objects.count())

        # test search
        response = self.get('api:places:search', data={'name': 'sky'})
        self.response_200()
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)

        response = self.get('api:places:search', data={'name': 'bar'})
        self.response_200()
        data = json.loads(response.content)
        self.assertEqual(len(data), 3)
