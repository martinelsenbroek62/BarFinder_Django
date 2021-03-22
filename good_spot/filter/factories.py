import factory
from good_spot.filter import models as filter_models


class TextFilterFieldFactory(factory.DjangoModelFactory):
    class Meta:
        model = filter_models.TextFilterField

    name = factory.Sequence(lambda n: 'text_filter_field_%s' % n)


class BoolFilterFieldFactory(factory.DjangoModelFactory):
    class Meta:
        model = filter_models.BoolFilterField

    name = factory.Sequence(lambda n: 'bool_filter_field_%s' % n)


class ChoiceFilterFieldFactory(factory.DjangoModelFactory):
    class Meta:
        model = filter_models.ChoiceFilterField

    name = factory.Sequence(lambda n: 'choice_filter_field_%s' % n)


class ChoiceFilterFieldOptionFactory(factory.DjangoModelFactory):
    class Meta:
        model = filter_models.ChoiceFilterFieldOption

    option = factory.Sequence(lambda n: 'option_%s' % n)


class PlaceChoiceFilterFieldFactory(factory.DjangoModelFactory):
    class Meta:
        model = filter_models.PlaceChoiceFilterField
