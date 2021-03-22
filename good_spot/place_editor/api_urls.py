from rest_framework import routers

from good_spot.place_editor import api

router = routers.DefaultRouter()

router.register(r'', api.PlaceEditorViewSet, base_name='place_editor')

urlpatterns = router.urls
