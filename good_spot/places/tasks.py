import pytz
from datetime import datetime, timedelta

from constance import config
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, F
from structlog import get_logger

from django.utils import timezone

from good_spot.common import definitions
from good_spot.events.models import UpdatingRule, UpdatingRuleRelation
from good_spot.places import models as places_models
from good_spot.populartimes.fill_place_data import fill_place, update_frequentation
from good_spot.taskapp.celery import app

log = get_logger()


@app.task()
def fill_place_async(place_id):
    log.msg("Task `fill_place_async` started.")
    fill_place(place_id)


@app.task()
def update_frequentation_async(place_id):
    log.msg("Task `update_frequentation_async` started.")
    update_frequentation(place_id)


@app.task
def run_fill_place_async():
    log.msg("Periodic task `run_fill_place_async` started.")
    for place in places_models.Place.objects.all():
        fill_place_async.delay(place.google_place_id)


@app.task
def run_update_frequentation_async():
    log.msg("Periodic task `run_update_frequentation_async` started.")
    for place in places_models.Place.objects.filter(update_populartimes=True):
        update_frequentation_async.delay(place.google_place_id)


def get_places_to_update(start, end, city):
    qs = UpdatingRule.objects.exclude(end__lt=start)
    qs = qs.filter(
        Q(rule="ONCE") &
        Q(start__gt=start) &
        Q(start__lte=end) |

        Q(rule="HOURLY") |

        Q(rule="DAILY") &
        Q(start_time__gt=start.time()) &
        Q(start_time__lte=end.time()) |

        Q(rule="WEEKLY") &
        Q(start__week_day=definitions.WEEKDAY_EXTRACT[definitions.WEEKDAY_DATETIME[start.weekday()]]) &
        Q(start_time__gt=start.time()) &
        Q(start_time__lte=end.time()) |

        Q(rule="MONTHLY") &
        Q(start__day=start.day) &
        Q(start_time__gt=start.time()) &
        Q(start_time__lte=end.time()) |

        Q(rule="YEARLY") &
        Q(start__month=start.month) &
        Q(start__day=start.day) &
        Q(start_time__gt=start.time()) &
        Q(start_time__lte=end.time())
    )

    updating_rules_pks = qs.values_list('id', flat=True)

    place_ct = ContentType.objects.get_for_model(places_models.Place)
    place_type_ct = ContentType.objects.get_for_model(places_models.PlaceType)

    places_pks = UpdatingRuleRelation.objects.filter(
        content_type=place_ct, rule_id__in=updating_rules_pks
    ).values_list('object_id', flat=True)

    place_types_pks = UpdatingRuleRelation.objects.filter(
        content_type=place_type_ct, rule_id__in=updating_rules_pks
    ).values_list('object_id', flat=True)

    places = places_models.Place.objects.filter(
        Q(city=city),
        Q(pk__in=places_pks) |
        Q(place_types__id__in=place_types_pks) &
        Q(city__is_active=True) &
        Q(is_published=True)
    ).distinct()

    return places


@app.task
def run_periodic_updates():
    log.info("\n\nPeriodic updates for scheduled events started.")

    now = timezone.now().replace(minute=0, second=0, microsecond=0)

    _process_timezones(now)


@app.task
def run_periodic_cleaning_expired_populartimes():
    for object in places_models.ActualPopularTimes.objects.all():
        if object.expire_at < timezone.now():
            object.delete()


def _process_timezones(current=None):
    if not current:
        current = timezone.now().replace(minute=0, second=0, microsecond=0)

    count_of_updated_places = 0

    for city in places_models.City.objects.filter(is_active=True):
        local_tz = pytz.timezone(city.timezone)

        local_end = current.astimezone(local_tz)
        local_start = local_end - timedelta(hours=1)

        utc_end = timezone.utc.localize(datetime(
            year=local_end.year,
            month=local_end.month,
            day=local_end.day,
            hour=local_end.hour,
            minute=local_end.minute
        ))
        utc_start = timezone.utc.localize(datetime(
            year=local_start.year,
            month=local_start.month,
            day=local_start.day,
            hour=local_start.hour,
            minute=local_start.minute
        ))

        places = get_places_to_update(utc_start, utc_end, city)
        count_of_updated_places += places.count()
        for place in places:
            update_frequentation_async.delay(place.google_place_id)

    return count_of_updated_places


@app.task
def run_hourly_updates():
    if config.UPDATE_PLACES_HOURLY:
        qs_places_all = places_models.Place.active_objects.all()
        active_places_pks = list(set(qs_places_all.values_list('pk', flat=True)))
        for place in places_models.Place.objects.filter(pk__in=active_places_pks).order_by(
                F('populartimes_updated_at').desc(nulls_first=True))[:300]:
            update_frequentation_async.delay(place.google_place_id)
