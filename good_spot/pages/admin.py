from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from good_spot.pages import models as pages_models


@admin.register(pages_models.Page)
class PageAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published')
    list_editable = ('is_published',)
