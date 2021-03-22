from rest_framework import routers

from good_spot.pages import api

router = routers.DefaultRouter()

router.register(r'', api.PageViewSet, base_name='pages')

urlpatterns = []
urlpatterns += router.urls
