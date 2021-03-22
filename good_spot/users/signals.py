from django.db.models.signals import post_save
from django.dispatch import receiver
from good_spot.users import models as users_models


@receiver(post_save, sender=users_models.User)
def update_user(sender, instance, created, **kwargs):
    if created:
        users_models.User.objects.filter(id=instance.id).update(username='user{}'.format(instance.id))
