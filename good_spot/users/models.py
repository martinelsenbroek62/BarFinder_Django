from cities_light.models import City
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from constance import config
from model_utils import Choices
from sorl.thumbnail import ImageField, get_thumbnail

from good_spot.places import models as places_models
from good_spot.filter import models as filter_models

OCCUPATION_CHOICES = Choices(
    (1, 'student', _('student')),
    (2, 'employee', _('employee'))
)


def avatars_folder(instance, filename):
    return '/'.join(['users/avatars', str(instance.id), filename])


class User(AbstractUser):
    occupation = models.PositiveSmallIntegerField(blank=True, null=True, choices=OCCUPATION_CHOICES)
    occupation_details = models.CharField(max_length=255, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    city = models.ForeignKey(City, null=True, blank=True)
    # go_out_days - list of integer. 0 - Monday, 6 - Sunday
    go_out_days = ArrayField(models.IntegerField(), null=True, blank=True)
    favorite_place_types = models.ManyToManyField(places_models.PlaceType)
    image = ImageField(null=True, blank=True, upload_to=avatars_folder)

    def __str__(self):
        return self.username

    @property
    def get_thumb(self):
        return get_thumbnail(self.image, str(config.MIN_IMAGE_SIZE), crop='noop',
                             quality=99).url if self.image else None


class Favorite(models.Model):
    user = models.ForeignKey(User, related_name='user_favorites')
    filter_field = models.ForeignKey(filter_models.FilterField)


class FavoriteChoiceFilterField(Favorite):
    value = models.ManyToManyField(filter_models.ChoiceFilterFieldOption)
