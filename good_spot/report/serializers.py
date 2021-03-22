from rest_framework import serializers

from good_spot.report.models import Report


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('email', 'message', 'app_version')
