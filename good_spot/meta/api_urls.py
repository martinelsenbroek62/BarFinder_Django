from django.conf.urls import url
from rest_framework import routers

from good_spot.meta import api

urlpatterns = [
    url(r'^android/$', api.AndroidVersion.as_view(), name='android_version'),
    url(r'^ios/$', api.IOSVersion.as_view(), name='ios_version'),
]
