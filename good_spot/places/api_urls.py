from django.conf.urls import url
from rest_framework import routers

from good_spot.places import api

router = routers.DefaultRouter()

router.register(r'filter', api.FilterViewSet, base_name='filters')
router.register(r'types', api.PlaceTypeViewSet, base_name='place_types')
router.register(r'', api.PlaceViewSet, base_name='places')

urlpatterns = [
    url(r'^cities/$', api.CityListAPIView.as_view(), name='cities'),
    url(r'^search/$', api.SearchListAPIView.as_view(), name='search'),
    url(r'^update_frequentation/$', api.FrequentationUpdateAPIView.as_view(), name='update_frequentation'),
    url(r'^report_place/(?P<pk>\d+)/$', api.PlaceReportAPIView.as_view(), name='report_place'),
]

urlpatterns += router.urls
