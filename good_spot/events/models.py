import datetime

from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext as _
from django.utils import timezone
from monthdelta import monthdelta
from model_utils import Choices
from model_utils.models import TimeStampedModel

from good_spot.common import definitions
from good_spot.common.definitions import WEEKDAY_DATETIME

from good_spot.places import models as places_models

RULE = Choices(
    ("ONCE", _("Once")),
    ("YEARLY", _("Yearly")),
    ("MONTHLY", _("Monthly")),
    ("WEEKLY", _("Weekly")),
    ("DAILY", _("Daily")),
    ("HOURLY", _("Hourly")),
)


class UpdatingRule(TimeStampedModel):
    title = models.CharField(_("title"), max_length=255)
    start = models.DateTimeField(_("start"), db_index=True)
    # This field auto populated on save. Needs for filtering.
    start_time = models.TimeField(_("Time to update"), null=True, blank=True)
    end = models.DateTimeField(_("end"), db_index=True, null=True, blank=True,
                               help_text=_("This rule will work until this date."))
    rule = models.CharField(_("frequency"), choices=RULE, max_length=10)

    # 0 - Monday
    weekday = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(6), MinValueValidator(0)],
        choices=WEEKDAY_DATETIME.items(),
        null=True,
        blank=True)

    def save(self, **kwargs):
        self.start_time = self.start.time()
        self.weekday = self.start.weekday()
        if self.rule == RULE.WEEKLY:
            self.title = "{} updating on {} at {}".format(
                self.rule,
                definitions.WEEKDAY_DATETIME[self.weekday],
                self.start_time
            )
        else:
            self.title = "{} updating at {}".format(self.rule, self.start_time)
        super(UpdatingRule, self).save(**kwargs)

    def __str__(self):
        return self.title

    @property
    def next_update(self):
        now = timezone.now()
        start = self.start
        next_update = start

        if (self.end and self.end < now) or (self.rule == "ONCE" and start < now):
            return "Expired"

        if start > now:
            return next_update

        if self.rule == "HOURLY":
            ##################################################################################

            next_update = now.replace(minute=start.minute, second=start.second)
            if next_update < now:
                next_update += datetime.timedelta(hours=1)

        elif self.rule == "DAILY":
            ##################################################################################

            next_update = now.replace(hour=start.hour, minute=start.minute, second=start.second)
            if next_update < now:
                next_update += datetime.timedelta(days=1)

        elif self.rule == "WEEKLY":
            ##################################################################################

            # weekday() return integer (Monday is 0 and Sunday is 6)
            next_update = now.replace(hour=start.hour, minute=start.minute, second=start.second)
            delta = (start.weekday() - now.weekday()) % 7
            next_update = next_update + datetime.timedelta(days=delta)
            if next_update < now:
                next_update += datetime.timedelta(weeks=1)

        elif self.rule == "MONTHLY":
            ##################################################################################

            next_update = now.replace(day=start.day, hour=start.hour, minute=start.minute, second=start.second)
            if next_update < now:
                next_update += monthdelta(1)

        elif self.rule == "YEARLY":
            ##################################################################################

            next_update = now.replace(month=start.month,
                                      day=start.day,
                                      hour=start.hour,
                                      minute=start.minute,
                                      second=start.second
                                      )
            if next_update < now:
                next_update += monthdelta(12)

        return next_update

    @property
    def related_objects_names(self):
        return self.rule_relations.values_list('get_name', flat=True)

    def all_related_places(self):
        places_pks = []
        for relation in self.rule_relations.all():
            places_pks += list(relation.get_places().values_list('id', flat=True))
        unique_places_pks = list(set(places_pks))
        return places_models.Place.objects.filter(pk__in=unique_places_pks)

    @property
    def all_related_places_count(self):
        return self.all_related_places().count()

    def all_active_related_places(self):
        active_related_places = self.all_related_places().filter(is_published=True, city__is_active=True)
        return active_related_places

    @property
    def all_active_related_places_count(self):
        return self.all_active_related_places().count()


class UpdatingRuleRelation(TimeStampedModel):
    rule = models.ForeignKey(UpdatingRule, on_delete=models.CASCADE, verbose_name=_("updating_rule"),
                             related_name='rule_relations')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.IntegerField(db_index=True)
    content_object = fields.GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return "{} {}".format(self.content_type, self.content_object)

    def get_places(self):
        if self.content_type == ContentType.objects.get_for_model(places_models.Place):
            return places_models.Place.objects.filter(pk=self.object_id)
        elif self.content_type == ContentType.objects.get_for_model(places_models.PlaceType):
            return self.content_object.place_set.all()
        return None
