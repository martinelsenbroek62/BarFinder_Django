import json

from test_plus import APITestCase
from good_spot.places import models as places_models
from good_spot.filter import models as filter_models
from good_spot.filter import factories as filter_factories


class FilterViewSetTestCase(APITestCase):

    def test_get_empty(self):
        response = self.get('api:places:filters-list')
        self.response_200()

        data = json.loads(response.content)
        self.assertEqual(len(data), places_models.PlaceType.objects.filter(is_active=True).count())

        for x in range(0, 5):
            filter_factories.BoolFilterFieldFactory()
            filter_factories.TextFilterFieldFactory()
            filter_factories.ChoiceFilterFieldFactory()

        for place_type in data:
            self.assertEqual(place_type['filters'], [])

        filter_field = filter_factories.ChoiceFilterFieldFactory(
            is_multi=True
        )

        for x in range(0, 5):
            filter_factories.ChoiceFilterFieldOptionFactory(
                choice_filter_field=filter_field
            )

        # TODO create places
        # place_filter_field = filter_factories.PlaceChoiceFilterFieldFactory(
        #     place=places_models.Place.objects.first(),
        #     field_type=filter_field
        # )
        # place_filter_field.value.add(filter_field.choice_options.first())

        # response = self.get('api:places:filters-list')
        # self.response_200()

        # data = json.loads(response.content)
        # self.assertEqual(len(data), places_models.PlaceType.objects.filter(is_active=True).count())
