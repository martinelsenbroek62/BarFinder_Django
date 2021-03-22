from rest_framework import routers

from good_spot.report.api import ReportViewSet

router = routers.DefaultRouter()

router.register(r'', ReportViewSet, base_name='reports')

urlpatterns = []
urlpatterns += router.urls
