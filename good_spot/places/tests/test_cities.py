import json

from test_plus import APITestCase
from cities_light import models as citieslight_model
from good_spot.places import models as places_models
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

    def test_get_empty(self):
        response = self.get('api:places:cities')
        self.response_200()

        data = json.loads(response.content)
        self.assertEqual(data, [])

    def test_get(self):
        for city in places_models.City.objects.all():
            place = factories.PlaceFactory(city=city)

        response = self.get('api:places:cities')
        self.response_200()

        data = json.loads(response.content)
        self.assertEqual(len(data), places_models.City.objects.count())

        # check if contains 'current_city'
        self.assertTrue('current_city' in data[0])

        # TODO test with lat and lng params
