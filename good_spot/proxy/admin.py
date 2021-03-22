from django.contrib import admin

from good_spot.proxy.models import Proxy


@admin.register(Proxy)
class ProxyAdmin(admin.ModelAdmin):
    list_display = ('external_ip', 'count', 'last_usage')
