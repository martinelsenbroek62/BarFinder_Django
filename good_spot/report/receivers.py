from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from structlog import get_logger

from good_spot.common.tasks import send_email_async

from .models import Report

log = get_logger()


@receiver(post_save, sender=Report)
def notify_admins_on_new_feedback(instance, **kwargs):
    if kwargs['created']:
        subject = _("New Feedback Received")
        log.msg("scheduling feedback notify email for %s" % (instance.email))
        body_html = render_to_string('emails/new_feedback.txt', {
            'report': instance
        }, request=None)
        send_email_async.delay(
            subject,
            body_html,
            None
        )
