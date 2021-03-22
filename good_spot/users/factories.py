import factory

from good_spot.users import models as users_models


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = users_models.User
