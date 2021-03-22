from django.conf.urls import url

from good_spot.images.api import PlaceImageListAPIView, ImageCroppedView

urlpatterns = [
    url(r'^$', PlaceImageListAPIView.as_view()),
    url(r'image-cropped/$', ImageCroppedView.as_view(), name='image_cropped'),
]
