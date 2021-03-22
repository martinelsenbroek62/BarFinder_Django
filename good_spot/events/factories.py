import factory
from good_spot.events import models as events_models


class UpdatingRuleFactory(factory.DjangoModelFactory):
    class Meta:
        model = events_models.UpdatingRule
