from modeltranslation.translator import translator, TranslationOptions
from good_spot.filter import models as filter_models


class FilterFieldTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(filter_models.FilterField, FilterFieldTranslationOptions)
translator.register(filter_models.ChoiceFilterField)
translator.register(filter_models.BoolFilterField)
translator.register(filter_models.TextFilterField)


class ChoiceFilterFieldOptionTranslationOptions(TranslationOptions):
    fields = ('option',)


translator.register(filter_models.ChoiceFilterFieldOption, ChoiceFilterFieldOptionTranslationOptions)


class PlaceTextFilterFieldTranslationOptions(TranslationOptions):
    fields = ('value',)


translator.register(filter_models.PlaceTextFilterField, PlaceTextFilterFieldTranslationOptions)
