from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from good_spot.filter import models


@admin.register(models.FilterField)
class FilterFieldAdmin(SortableAdminMixin, TranslationAdmin):
    list_display = ('name', 'polymorphic_ctype',
                    'is_public', 'is_filter', 'is_shown_in_short_description', 'is_shown_in_about_place',
                    'is_shown_in_features')
    list_filter = ('place_type',)


@admin.register(models.BoolFilterField)
class BoolFilterFieldAdmin(TranslationAdmin):
    list_display = ('name',)


@admin.register(models.TextFilterField)
class TextFilterFieldAdmin(TranslationAdmin):
    list_display = ('name',)


class ChoiceFilterFieldOptionTabularInline(admin.TabularInline):
    model = models.ChoiceFilterFieldOption


@admin.register(models.ChoiceFilterField)
class ChoiceFilterFieldAdmin(TranslationAdmin):
    inlines = (ChoiceFilterFieldOptionTabularInline,)
    list_display = ('name',)


@admin.register(models.PlaceFilterField)
class PlaceFilterFieldAdmin(admin.ModelAdmin):
    list_display = ('field_type', 'place', 'polymorphic_ctype')


@admin.register(models.PlaceBoolFilterField)
class PlaceFilterFieldAdmin(admin.ModelAdmin):
    pass


@admin.register(models.PlaceTextFilterField)
class PlaceFilterFieldAdmin(admin.ModelAdmin):
    pass


@admin.register(models.PlaceChoiceFilterField)
class PlaceFilterFieldAdmin(admin.ModelAdmin):
    pass
