from adminsortable2.admin import SortableInlineAdminMixin
from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext as _
from prettyjson import PrettyJSONWidget
from structlog import get_logger
from modeltranslation.admin import TranslationAdmin

from good_spot.filter import admin_inlines
from good_spot.events.models import UpdatingRuleRelation
from good_spot.images.models import PlaceImage
from good_spot.places.models import (Place, PlaceType, City, Frequentation,
                                     ActualPopularTimes)
from good_spot.places.tasks import fill_place_async, update_frequentation_async
from good_spot.places.widgets import PopularTimesWidget
from good_spot.place_editor import views as place_editor_views
from good_spot.events import views as events_views

log = get_logger()


def update_frequentation_action(modeladmin, request, queryset):
    log.msg("Admin action `update_frequentation_action` ran.")
    for place in queryset:
        update_frequentation_async.delay(place.google_place_id)


update_frequentation_action.short_description = _("Update frequentation")


def update_google_data_action(modeladmin, request, queryset):
    log.msg("Admin action `update_google_data_action` ran.")
    for place in queryset:
        fill_place_async.delay(place.google_place_id)


update_google_data_action.short_description = _("Update place from Google")


class PlacePopularTimeFilter(SimpleListFilter):
    title = _('Popular times')
    parameter_name = 'pop_time'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Has popular times')),
            ('no', _('Does not have popular times')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(populartimes__isnull=False)
        if self.value() == 'no':
            return queryset.filter(populartimes__isnull=True)


class PlaceFrequentationFilter(SimpleListFilter):
    title = _('Frequentation')
    parameter_name = 'frequentation'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Has actual popular times')),
            ('no', _('Does not have actual popular times')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(actualpopulartimes__isnull=False)
        if self.value() == 'no':
            return queryset.filter(actualpopulartimes__isnull=True)


class UpdatingRuleRelationInline(GenericTabularInline):
    model = UpdatingRuleRelation
    exclude = ('event_relation',)
    extra = 1


class PlaceImageInline(SortableInlineAdminMixin, admin.TabularInline):
    model = PlaceImage
    exclude = ('thumbnail',)
    extra = 1


class PlaceAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'populartimes': PopularTimesWidget(attrs={'initial': 'parsed'})
        }


@admin.register(Place)
class PlaceAdmin(TranslationAdmin):
    change_form_template = "admin/place_change_form.html"
    form = PlaceAdminForm
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget(attrs={'initial': 'parsed'})}
    }
    list_display = ('name', 'address', 'google_place_id', 'city', 'is_published',
                    'get_place_types', 'extended_place_types', 'has_popular_times', 'google_rating',
                    'update_populartimes')
    list_filter = ('city', 'place_types', 'is_published', 'google_price_level',
                   'update_populartimes', PlacePopularTimeFilter, PlaceFrequentationFilter)
    list_editable = ('is_published',)
    search_fields = ('name', 'google_place_id')
    list_per_page = 50
    fieldsets = (
        (None, {
            'fields': ('google_place_id', 'is_published')
        }),
        (_("Data from Google Place API"), {
            'fields': ('city', 'name', 'block_name', 'place_types', 'block_place_types', 'extended_place_types',
                       'google_rating', 'block_google_rating', 'google_price_level', 'block_google_price_level',
                       'location', 'block_location', 'address', 'block_address', 'website', 'block_website',
                       'phone', 'block_phone', 'open_hours', 'google_data'),
        }),
        (_("Custom data"), {
            'fields': ('long_description', 'special_event', 'is_gay_friendly'),
        }),
        (_("Frequentation"), {
            'fields': ('update_populartimes', 'populartimes'),
        }),
    )
    actions = [update_google_data_action, update_frequentation_action]

    class Media:
        js = (
            'js/admin/place_change.js',
        )

    def get_urls(self):
        urls = super(PlaceAdmin, self).get_urls()
        extra_urls = [
            url(r'^(?P<pk>\d+)/change/$', place_editor_views.PlaceDetailView.as_view(), name='place_editor_detail'),
            url(r'^add/$', place_editor_views.PlaceCreateView.as_view(), name='place_editor_create'),
            url(r'^statistic/$', events_views.EventSchedule.as_view(), name='rules_schedule'),
        ]
        return extra_urls + urls

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.inlines = (
            admin_inlines.PlaceChoiceFilterFieldInline,
            admin_inlines.PlaceTextFilterFieldInline,
            admin_inlines.PlaceBoolFilterFieldInline,
            UpdatingRuleRelationInline,)
        return self.changeform_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            fill_place_async.delay(obj.google_place_id)
            update_frequentation_async.delay(obj.google_place_id)

    def has_popular_times(self, obj):
        if obj.populartimes is None:
            return ''
        return obj.populartimes_updated_at.strftime("%Y-%m-%d %H:%M") if obj.populartimes_updated_at else True
        has_popular_times.short_description = _("Has popular times")


@admin.register(PlaceType)
class PlaceTypeAdmin(TranslationAdmin):
    list_display = ('name', 'is_active', 'get_list_of_cities', 'is_default')
    prepopulated_fields = {"slug": ("name",)}
    inlines = (UpdatingRuleRelationInline,)


class PlaceTypeTabularInline(admin.TabularInline):
    model = PlaceType.active_in_cities.through


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget(attrs={'initial': 'parsed'})}
    }
    list_display = ('city', 'point', 'timezone', 'is_active', 'is_default')
    list_editable = ('is_active', 'is_default',)
    inlines = (PlaceTypeTabularInline,)


@admin.register(Frequentation)
class FrequentationAdmin(admin.ModelAdmin):
    list_display = ('place', 'value', 'created', 'is_hidden', 'user')
    ordering = ('-is_hidden',)
    list_editable = ('is_hidden',)
    list_per_page = 15


class ActualPopularTimesAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            'value': PopularTimesWidget(attrs={'initial': 'parsed'})
        }


@admin.register(ActualPopularTimes)
class ActualPopularTimesAdmin(admin.ModelAdmin):
    form = ActualPopularTimesAdminForm
    list_display = ('place',)
