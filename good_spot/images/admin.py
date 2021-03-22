from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from good_spot.images.models import PlaceImage


@admin.register(PlaceImage)
class PlaceImageAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'place', 'created')
    fields = ('place', 'image')
