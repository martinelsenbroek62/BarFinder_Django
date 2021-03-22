from django.db import models

from django.utils.translation import ugettext as _
from model_utils.models import TimeStampedModel
from polymorphic.models import PolymorphicModel
from django.contrib.postgres.fields import JSONField

from good_spot.places import models as places_models

FILTER_MODEL_MAPPING = {
    'PlaceBoolFilterField': 'BoolFilterField',
    'PlaceTextFilterField': 'TextFilterField',
    'PlaceChoiceFilterField': 'ChoiceFilterField'
}


class FilterField(TimeStampedModel, PolymorphicModel):
    name = models.CharField(_("Name"), max_length=50)
    place_type = models.ManyToManyField(places_models.PlaceType,
                                        help_text=_("This field will be available for chosen places types."))
    is_public = models.BooleanField(_("Is public?"), default=True)
    is_filter = models.BooleanField(_("Is filter?"), default=False, help_text=_(
        "Use this field to generate filters."))
    is_shown_in_features = models.BooleanField(_("Title: Bold Upper part of short description"), default=False,
                                               help_text=_(
                                                   "Use this field to generate features displaying under the title of place."))
    is_shown_in_short_description = models.BooleanField(_("Sub title: Sub part of short description"),
                                                        default=False, help_text=_("Use this field to generate `Short "
                                                                                   "Description` section on detail "
                                                                                   "screen."))
    is_shown_in_about_place = models.BooleanField(_("Show in About Place section"), default=False, help_text=_(
        "Use this field to generate `About Place` section on detail screen."))

    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    class Meta:
        verbose_name = _("ALL FILTERS--" + "-" * 50)
        verbose_name_plural = _("ALL FILTERS--" + "-" * 50)
        ordering = ('order',)

    def __str__(self):
        place_types_str = ', '.join(list(self.place_type.values_list('name', flat=True)))
        return "{} ({})".format(self.name, place_types_str)


class BoolFilterField(FilterField):
    class Meta:
        verbose_name = _("Fields BOOLEAN")
        verbose_name_plural = _("Fields BOOLEAN")

    def __str__(self):
        return "{} (boolean)".format(self.name)


class TextFilterField(FilterField):
    class Meta:
        verbose_name = _("Fields TEXTUAL")
        verbose_name_plural = _("Fields TEXTUAL")

    def __str__(self):
        return "{} (text)".format(self.name)


class ChoiceFilterField(FilterField):
    is_multi = models.BooleanField(default=False, help_text=_("If you mark this field as `multi` user can select more "
                                                              "then one choice in the Filter in the app."))
    is_users_tastes = models.BooleanField(_("Lets user to choose his tastes in profile."), default=False, help_text=_(
        "If checked user will see the section named as this filter field with options to choose his own tastes."
    ))

    class Meta:
        verbose_name = _("Fields SELECTIVE")
        verbose_name_plural = _("Fields SELECTIVE")

    def __str__(self):
        return "{} (choice)".format(self.name)


class ChoiceFilterFieldOption(TimeStampedModel):
    choice_filter_field = models.ForeignKey(ChoiceFilterField, related_name="choice_options")
    option = models.CharField(max_length=100)

    class Meta:
        unique_together = ('choice_filter_field', 'option')
        ordering = ('option',)

    def __str__(self):
        return self.option


class PlaceFilterField(TimeStampedModel, PolymorphicModel):
    place = models.ForeignKey(places_models.Place,
                              related_name='place_filter_field')
    field_type = models.ForeignKey(FilterField,
                                   related_name='place_filter_field')

    class Meta:
        verbose_name = _("PLACE FIELDS" + "-" * 50)
        verbose_name_plural = _("PLACE FIELDS" + "-" * 50)
        unique_together = ('place', 'field_type')

    def __str__(self):
        return "`{}` for `{}`".format(self.field_type.name, self.place)


class PlaceChoiceFilterField(PlaceFilterField):
    value = models.ManyToManyField(ChoiceFilterFieldOption, blank=True)

    class Meta:
        verbose_name = _("Place fields SELECTIVE")
        verbose_name_plural = _("Place fields SELECTIVE")


class PlaceBoolFilterField(PlaceFilterField):
    value = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Place fields BOOLEAN")
        verbose_name_plural = _("Place fields BOOLEAN")


class PlaceTextFilterField(PlaceFilterField):
    value = models.CharField(max_length=255)

    class Meta:
        verbose_name = _("Place fields TEXTUAL")
        verbose_name_plural = _("Place fields TEXTUAL")
