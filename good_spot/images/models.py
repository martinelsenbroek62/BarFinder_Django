import uuid

import os

from django.db import models
from django.utils.translation import ugettext as _
from model_utils.models import TimeStampedModel

from good_spot.places.models import Place


def user_directory_path(instance, filename):
    name, ext = os.path.splitext(filename)
    name = uuid.uuid4()
    return 'images/{}{}'.format(name, ext)


class PlaceImage(TimeStampedModel):
    place = models.ForeignKey(Place, related_name='place_images')
    image = models.ImageField(_('Image'), upload_to=user_directory_path)
    # thumbnail creates by lambda function
    thumbnail = models.ImageField(_('Thumbnail'), upload_to='resized-images/', blank=True, null=True)

    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta(object):
        ordering = ['order']

    def __str__(self):
        return '{}. {}'.format(self.id, self.place)
