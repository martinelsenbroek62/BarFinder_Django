from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from good_spot.filter import models as filter_models
from good_spot.places import models as places_models


@receiver(post_save, sender=filter_models.PlaceBoolFilterField)
def remove_if_false(sender, instance, created, **kwargs):
    if not instance.value:
        instance.delete()


@receiver(m2m_changed, sender=places_models.Place.place_types.through)
def update_place_filter_fields_on_m2m_changed(sender, instance, **kwargs):
    if kwargs['action'] == 'post_remove':
        filter_models.PlaceChoiceFilterField.objects.filter(
            place=instance,
            field_type__place_type__in=kwargs['pk_set']
        ).exclude(
            field_type__place_type__in=instance.place_types.all()
        ).delete()

        filter_models.PlaceBoolFilterField.objects.filter(
            place=instance,
            field_type__place_type__in=kwargs['pk_set']
        ).exclude(
            field_type__place_type__in=instance.place_types.all()
        ).delete()

        filter_models.PlaceTextFilterField.objects.filter(
            place=instance,
            field_type__place_type__in=kwargs['pk_set']
        ).exclude(
            field_type__place_type__in=instance.place_types.all()
        ).delete()


@receiver(post_save, sender=places_models.Frequentation)
def apply_frequentation_from_user(sender, instance, **kwargs):
    if instance.hidden_tracker.has_changed('is_hidden') and not instance.is_hidden:
        instance.place.actualize_popular_time(frequentation=instance)


@receiver(post_save, sender=places_models.City)
def reset_city_is_default(sender, instance, **kwargs):
    if instance.is_default:
        places_models.City.objects.exclude(pk=instance.pk).update(is_default=False)
