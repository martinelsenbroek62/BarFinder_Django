from django.conf.urls import url
from rest_framework import routers

from good_spot.users import api

router = routers.DefaultRouter()

router.register(r'', api.UserViewSet, base_name='users')

urlpatterns = [
    url(r'^facebook/$', api.FacebookLogin.as_view(), name='facebook'),
    url(r'^search_city/$', api.SearchCityListAPIView.as_view(), name='search'),
]

urlpatterns += router.urls
