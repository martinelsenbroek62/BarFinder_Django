from django.conf.urls import url

from good_spot.common.views import HealthCheckView

urlpatterns = [
    url(r'^checker/$', HealthCheckView.as_view()),
]
