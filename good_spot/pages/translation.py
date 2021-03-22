from modeltranslation.translator import TranslationOptions, translator
from good_spot.pages import models as pages_models


class PageTranslationOptions(TranslationOptions):
    fields = ('title', 'short_description', 'text')


translator.register(pages_models.Page, PageTranslationOptions)
