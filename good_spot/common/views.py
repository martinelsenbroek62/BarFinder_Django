# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf import settings
from django.http.response import HttpResponse
from django.views.generic import View


class HealthCheckView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(settings.HEALTH_CHECK_BODY, status=200)
