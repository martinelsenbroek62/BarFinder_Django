from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext as _
from model_utils.models import TimeStampedModel

from good_spot.places.models import Place


class Populartimes(TimeStampedModel):
    place = models.ForeignKey(Place, related_name='place_poptimes')
    populartimes = JSONField(null=True, blank=True)

    class Meta:
        verbose_name_plural = _("Populartimes")

    def __str__(self):
        return "\"{}\" updated at: {}".format(self.place.name, self.created)
