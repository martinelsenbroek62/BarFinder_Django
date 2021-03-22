from rest_framework import viewsets, mixins

from good_spot.report.serializers import ReportSerializer


class ReportViewSet(mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = ReportSerializer
