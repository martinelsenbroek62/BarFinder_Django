from cities_light import models as cities_light_models
from modeltranslation.translator import translator, TranslationOptions
from good_spot.places import models as place_models


class PlaceTypeTranslationOptions(TranslationOptions):
    fields = ('name', 'name_plural')


translator.register(place_models.PlaceType, PlaceTypeTranslationOptions)


class PlaceTranslationOptions(TranslationOptions):
    fields = ('name', 'address', 'special_event')


translator.register(place_models.Place, PlaceTranslationOptions)


class CityTranslationOptions(TranslationOptions):
    fields = ('name', 'country_name')


translator.register(place_models.City, CityTranslationOptions)
