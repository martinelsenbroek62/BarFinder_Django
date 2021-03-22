from datetime import timedelta

import pytz
from cities_light.models import City
from constance import config
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.db.models import F
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from model_utils import FieldTracker
from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField
from structlog import get_logger

from good_spot.places.definitions import DAYS_OF_WEEK
from good_spot.populartimes.update_data import populartimes_extrapolation
from good_spot.events import models as rules_models

log = get_logger()


class CityManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            is_active=True
        )


class City(models.Model):
    city = models.OneToOneField(City, null=True)
    timezone = models.CharField(max_length=40, choices=((tz, tz) for tz in pytz.common_timezones))
    name_variants = JSONField(null=True, blank=True)
    is_active = models.BooleanField(_("Active?"), default=True,
                                    help_text=_("Do you want to show this city in dropdown menu in app?"))
    name = models.CharField(max_length=200, db_index=True, blank=True)
    # todo name and country_name are duplicated
    country_name = models.CharField(max_length=200, blank=True)
    point = gis_models.PointField(blank=True)
    is_default = models.BooleanField(default=False, verbose_name=_('If checked this city will default in application '
                                                                   'in case when user disallowed GPS.'))

    objects = models.Manager()
    active_objects = CityManager()

    class Meta:
        verbose_name_plural = _('Application cities')

    def __str__(self):
        return self.city.name if self.city else ''

    def save(self, **kwargs):
        self.name = self.city.name
        self.country_name = self.city.country.name
        self.point = Point(
            float(self.city.longitude),
            float(self.city.latitude)
        )
        super(City, self).save(**kwargs)


class PlaceType(models.Model):
    name = models.CharField(_("Place type"), max_length=20)
    name_plural = models.CharField(_("Place type (plural)"), max_length=20, blank=True)
    slug = models.SlugField(_("Slug"), max_length=10, null=True, blank=True, auto_created=True)
    is_active = models.BooleanField(_("Is active?"), default=True, help_text=_("Show in app."))
    active_in_cities = models.ManyToManyField(City, blank=True)
    is_default = models.BooleanField(_("Is default to show in main screen?"), default=False)

    def __str__(self):
        return self.name

    def clean(self):
        if self.is_default and PlaceType.objects.filter(is_default=True).exclude(pk=self.pk).exists():
            raise ValidationError(
                {"is_default": _('There is can be only one default place type. It is already exists.')})

    def get_rules(self):
        ct = ContentType.objects.get_for_model(self)

        rules_list_ids = list(rules_models.UpdatingRuleRelation.objects.filter(
            content_type=ct,
            object_id=self.id
        ).values_list('rule_id', flat=True))
        rules = rules_models.UpdatingRule.objects.filter(id__in=rules_list_ids)
        return rules

    def get_list_of_cities(self):
        return list(self.active_in_cities.values_list('name', flat=True))


class PlaceManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset().filter(
            is_published=True,
            city__is_active=True,
            place_types__is_active=True,
            place_types__active_in_cities__in=City.active_objects.filter(is_active=True),
            place_types__active_in_cities=F('city_id')
        )
        return qs


class Place(TimeStampedModel):
    # Google Place API data
    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.SET_NULL)
    block_city = models.BooleanField(default=False, help_text=_(
        "Block <b>City</b> from updating from the Google Places API.<br>"
        "It means, if you change <b>City</b> manually, it won't be rewritten from "
        "the Google Places API after updating."
    ))
    name = models.CharField(_("Place name"), max_length=255, null=True, blank=True, db_index=True)
    block_name = models.BooleanField(default=False, help_text=_(
        "Block <b>Place name</b> from updating from the Google Places API.<br>"
        "It means, if you change <b>Place name</b> manually, it won't be rewritten from "
        "the Google Places API after updating."
    ))
    place_types = models.ManyToManyField(PlaceType, blank=True)
    block_place_types = models.BooleanField(default=False,
                                            help_text=_(
                                                "Block <b>Place types</b> from updating from the Google Places API.<br>"
                                                "It means, if you change <b>Place types</b> manually, it won't be rewritten from the Google Places API after updating."))
    google_place_id = models.CharField(_("Place ID"), max_length=255, unique=True)
    google_rating = models.FloatField(null=True, blank=True,
                                      validators=[MaxValueValidator(5.0), ])
    block_google_rating = models.BooleanField(default=False,
                                              help_text=_(
                                                  "Block <b>Google rating</b> from updating from the Google Places API.<br>"
                                                  "It means, if you change <b>Google rating</b> manually, it won't be rewritten from the Google Places API after updating."))
    google_price_level = models.PositiveSmallIntegerField(null=True, blank=True,
                                                          validators=[MinValueValidator(0), MaxValueValidator(4)])
    block_google_price_level = models.BooleanField(default=False,
                                                   help_text=_(
                                                       "Block <b>Google price level</b> from updating from the Google Places API.<br>"
                                                       "It means, if you change <b>Google price level</b> manually, it won't be rewritten from the Google Places API after updating."))
    location = gis_models.PointField(null=True, blank=True)
    block_location = models.BooleanField(default=False,
                                         help_text=_(
                                             "Block <b>Location</b> from updating from the Google Places API.<br>"
                                             "It means, if you change <b>Location</b> manually, it won't be rewritten from the Google Places API after updating."))
    address = models.CharField(_("Place address"), max_length=255, null=True, blank=True)
    block_address = models.BooleanField(default=False,
                                        help_text=_("Block <b>Address</b> from updating from the Google Places API.<br>"
                                                    "It means, if you change <b>Address</b> manually, it won't be rewritten from the Google Places API after updating."))
    website = models.URLField(_("Website"), max_length=255, null=True, blank=True)
    block_website = models.BooleanField(default=False,
                                        help_text=_("Block <b>Website</b> from updating from the Google Places API.<br>"
                                                    "It means, if you change <b>Website</b> manually, it won't be rewritten from the Google Places API after updating."))
    phone = PhoneNumberField(null=True, blank=True)
    block_phone = models.BooleanField(default=False,
                                      help_text=_("Block <b>Phone</b> from updating from the Google Places API.<br>"
                                                  "It means, if you change <b>Phone</b> manually, it won't be rewritten from the Google Places API after updating."))
    open_hours = JSONField(null=True, blank=True)
    # Google Place API response
    google_data = JSONField(null=True, blank=True)

    # Frequentation
    update_populartimes = models.BooleanField(default=True)
    populartimes = JSONField(null=True, blank=True)
    extended_place_types = JSONField(null=True, blank=True)
    populartimes_updated_at = models.DateTimeField(models.DateTimeField, blank=True, null=True)

    # custom data
    long_description = models.TextField(blank=True)
    special_event = models.CharField(_("Special event"), max_length=255, blank=True, null=True)
    is_gay_friendly = models.BooleanField(default=False)

    is_published = models.BooleanField(default=True)

    # TODO remove `short_description` and `features` from web and mobiles apps. Unsupported fiedls.
    # short_description is calculated in post_signal for model PlaceField
    # in PlaceModelSerializer return as json
    # in PlaceRetrieveModelSerializer return as string
    short_description = JSONField(null=True, blank=True)

    # short_description is calculated in post_signal for model PlaceField
    # in PlaceModelSerializer return as json
    # in PlaceRetrieveModelSerializer return as list
    features = JSONField(null=True, blank=True)

    objects = models.Manager()
    active_objects = PlaceManager()

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return "{} [{}]".format(self.name, self.google_place_id)

    def get_place_types(self):
        return list(self.place_types.values_list('name', flat=True))

    def actualize_popular_time(self, frequentation=None):
        log.msg("Actualizing popular time started.")
        # this method will update populartimes using frequentation
        if not self.populartimes:
            log.msg("Actualizing popular time interrupted because populartimes does not exist.")
            return

        if not frequentation:
            log.msg("Actualizing popular time interrupted because frequentation does not exist.")
            return

        try:
            tz = pytz.timezone(self.city.timezone)
        except Exception:
            log.error("Can not recognize timezone.")
            return

        day = frequentation.created.astimezone(tz).strftime("%A")
        if not day in DAYS_OF_WEEK:
            log.msg("Actualizing popular time interrupted because the day is wrong.")
            return

        hour = int(frequentation.created.astimezone(tz).strftime("%H"))
        if not 0 <= hour < 24:
            log.msg("Actualizing popular time interrupted because the hour is wrong.")
            return

        live_value = frequentation.value
        if not live_value:
            log.msg("Actualizing popular time interrupted because frequentation.value does not exist.")
            return

        populartimes = self.populartimes

        actual_populartimes = populartimes_extrapolation(
            populartimes=populartimes,
            live=live_value,
            day=day,
            hour=hour
        )
        if hasattr(self, 'actualpopulartimes'):
            self.actualpopulartimes.value = actual_populartimes
            self.actualpopulartimes.expire_at = now() + timedelta(hours=config.LIVE_IS_ACTUAL_FOR_NUM_HOURS)
            self.actualpopulartimes.save()
            log.msg("Actual populartimes for place {} updated.".format(self.name))
        else:
            ActualPopularTimes.objects.create(
                value=actual_populartimes,
                expire_at=now() + timedelta(hours=config.LIVE_IS_ACTUAL_FOR_NUM_HOURS),
                place=self
            )
            log.msg("Actual populartimes for place {} created.".format(self.name))

    @property
    def preview(self):
        if self.place_images.exists():
            place_image = self.place_images.first()
            if place_image:
                preview = place_image.thumbnail or place_image.image
                return preview.url
        return None

    def get_rules(self):
        ct = ContentType.objects.get_for_model(self)

        rules_list_ids = list(rules_models.UpdatingRuleRelation.objects.filter(
            content_type=ct,
            object_id=self.id
        ).values_list('rule_id', flat=True))
        rules = rules_models.UpdatingRule.objects.filter(id__in=rules_list_ids)
        return rules

    def get_place_types_rules(self):
        ct = ContentType.objects.get_for_model(PlaceType)

        rules_list_ids = list(rules_models.UpdatingRuleRelation.objects.filter(
            content_type=ct,
            object_id__in=list(self.place_types.values_list("id", flat=True))
        ).values_list('rule_id', flat=True))
        rules = rules_models.UpdatingRule.objects.filter(id__in=rules_list_ids)
        return rules

    def get_grouped_short_description(self):
        place = self
        place_fields = place.place_filter_field.select_related(
            'field_type'
        ).filter(
            field_type__is_shown_in_short_description=True
        ).order_by('field_type__order')

        grouped_short = {}
        for place_type in place.place_types.all():
            place_fields_filtered = place_fields.filter(field_type__place_type=place_type)
            res = []
            for pf in place_fields_filtered:
                if pf.polymorphic_ctype == ContentType.objects.get(model='placechoicefilterfield'):
                    res += list(pf.value.values_list('option', flat=True))
                elif pf.polymorphic_ctype == ContentType.objects.get(model='placeboolfilterfield') and pf.value:
                    res.append(pf.field_type.name)
                elif pf.polymorphic_ctype == ContentType.objects.get(model='placetextfilterfield') and pf.value:
                    res.append(pf.value)
            short_description = ', '.join(res)
            if short_description:
                grouped_short[place_type.slug] = short_description
        return grouped_short

    def get_grouped_features(self):
        place = self
        place_fields = place.place_filter_field.select_related(
            'field_type'
        ).filter(
            field_type__is_shown_in_features=True
        ).order_by(
            'field_type__order'
        )
        grouped_features = {}
        for place_type in place.place_types.all():
            place_fields_filtered = place_fields.filter(field_type__place_type=place_type)
            res = []
            for pf in place_fields_filtered:
                if pf.polymorphic_ctype == ContentType.objects.get(model='placechoicefilterfield'):
                    res += list(pf.value.values_list('option', flat=True))
                elif pf.polymorphic_ctype == ContentType.objects.get(model='placeboolfilterfield') and pf.value:
                    res.append(pf.field_type.name)
                elif pf.polymorphic_ctype == ContentType.objects.get(model='placetextfilterfield') and pf.value:
                    res.append(pf.value)
            if res:
                grouped_features[place_type.slug] = res
        return grouped_features


class ActualPopularTimes(TimeStampedModel):
    value = JSONField()
    expire_at = models.DateTimeField()
    place = models.OneToOneField(Place)

    class Meta:
        verbose_name_plural = _("Actual popular times")


class Frequentation(TimeStampedModel):
    place = models.ForeignKey(Place, related_name='frequentations')
    value = models.PositiveSmallIntegerField()
    origin_from_user = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    hidden_tracker = FieldTracker(fields=['is_hidden', ])

    class Meta:
        ordering = ('place', '-created')
