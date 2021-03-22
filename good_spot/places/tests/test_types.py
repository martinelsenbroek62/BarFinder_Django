import json

from test_plus import APITestCase


class PlaceTypeViewSetTestCase(APITestCase):
    fixtures = [
        'good_spot/fixtures/place_types.json',
    ]

    def test_get_empty(self):
        response = self.get('api:places:place_types-list')
        self.response_200()

        data = json.loads(response.content)
        self.assertEqual(data, [])
