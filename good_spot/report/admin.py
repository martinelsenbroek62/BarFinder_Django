from django.contrib import admin

from good_spot.report.models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_filter = ('created',)
    search_fields = ('email', 'app_version')
