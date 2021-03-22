import json

from django.urls import reverse
from test_plus import APITestCase
from good_spot.users import factories as users_factories


class UserViewSetTestCase(APITestCase):
    user_factory = users_factories.UserFactory

    def setUp(self):
        self.user = self.make_user()
        self.user2 = users_factories.UserFactory()
        self.view_url = reverse('api:users:users-detail', args=[self.user.id, ])

    def test_permissions(self):
        self.get(self.view_url)
        self.response_401()

        self.client.force_authenticate(self.user)
        self.get(self.view_url)
        self.response_200()

        self.get(reverse('api:users:users-detail', args=[self.user2.id]))
        self.response_403()

        self.patch(self.view_url, data={}, extra={'format': 'json'})
        self.response_200()

        self.patch(reverse('api:users:users-detail', args=[self.user2.id]), data={}, extra={'format': 'json'})
        self.response_403()
