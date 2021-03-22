from django.contrib import admin
from django import forms
from constance import config
from django.utils.html import format_html

from good_spot.events.models import UpdatingRule, UpdatingRuleRelation
from good_spot.proxy import models as proxy_model


class UpdatingRuleAdminForm(forms.ModelForm):
    class Meta:
        model = UpdatingRule
        fields = ('start', 'end', 'rule')


# TODO commented because celery task for events are commented
# @admin.register(UpdatingRule)
class UpdatingRuleAdmin(admin.ModelAdmin):
    list_display = ("title", "start", "end", "rule",
                    "next_update",
                    "all_related_places_count",
                    "all_active_related_places_count",
                    "weekday")
    list_filter = ("start", "rule")
    readonly_fields = ("weekday", "start_time")
    ordering = ('weekday',)
    form = UpdatingRuleAdminForm

    def _get_updates_count(self):
        return int(60 / config.DELAY_BETWEEN_PROXY_REQUESTS_IN_MINUTES
                   * proxy_model.Proxy.objects.count())

    def all_active_related_places_count(self, obj):
        if obj.all_active_related_places_count > self._get_updates_count():
            return format_html("<strong style='color: red;'>{}</strong>".format(obj.all_active_related_places_count))
        else:
            return obj.all_active_related_places_count

    def changelist_view(self, request, extra_context=None):
        extra_context = {
            'max_requests_per_hour': config.MAX_REQUESTS_PER_HOUR,
            'delay_in_min': config.DELAY_BETWEEN_PROXY_REQUESTS_IN_MINUTES,
            'proxies_count': proxy_model.Proxy.objects.count(),
            'updates_count': self._get_updates_count()
        }
        return super(UpdatingRuleAdmin, self).changelist_view(request, extra_context=extra_context)


# TODO commented because celery task for events are commented
# @admin.register(UpdatingRuleRelation)
class UpdatingRuleRelationAdmin(admin.ModelAdmin):
    pass
