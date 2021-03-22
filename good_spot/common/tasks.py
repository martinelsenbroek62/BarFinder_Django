# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.mail import EmailMessage
from django.conf import settings
from structlog import get_logger

from good_spot.taskapp.celery import app

log = get_logger()


@app.task()
def send_email_async(subject, body_html, email):
    log.msg("Task `send_email_async` started.")
    emails = [email] if email else list(settings.ADMINS)
    msg = EmailMessage(
        subject,
        body_html,
        settings.DEFAULT_FROM_EMAIL,
        emails,
    )
    msg.content_subtype = 'html'
    msg.send(fail_silently=True)
