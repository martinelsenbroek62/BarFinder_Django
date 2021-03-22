# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import include, url
from drf_skd_tools.swagger.views import get_swagger_view

urlpatterns = [
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^docs/$', get_swagger_view(title='MyGoodSpot API')),
    url(r'^places/', include("good_spot.places.api_urls", namespace="places")),
    url(r'^images/', include("good_spot.images.api_urls", namespace="images")),
    url(r'^report/', include("good_spot.report.api_urls", namespace="report")),
    url(r'^place_editor/', include("good_spot.place_editor.api_urls", namespace="editor")),
    url(r'^users/', include("good_spot.users.api_urls", namespace="users")),
    url(r'^pages/', include("good_spot.pages.api_urls", namespace="pages")),
    url(r'^meta/',include("good_spot.meta.api_urls",namespace="meta")),
]
