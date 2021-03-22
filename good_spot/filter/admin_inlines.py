from django.forms import BaseInlineFormSet
from django import forms
from django.apps import apps
from django.contrib.admin import widgets
from django.contrib import admin
from django.forms.widgets import CheckboxSelectMultiple, SelectMultiple
from django.utils.text import format_lazy

from good_spot.filter import models as filter_models


class FilterBaseInlineFormSet(BaseInlineFormSet):

    def _get_extra_init(self, queryset, obj):
        # Here we are getting available filter fields for current object to populate initial formset.

        # get place types of place
        place_types = obj.place_types.all()
        # get existing place field
        qs = queryset.filter(**{self.fk.name: self.instance})
        # get filter fields available for this place types
        if self.model.__name__ in filter_models.FILTER_MODEL_MAPPING:
            filter_model = apps.get_model('filter', filter_models.FILTER_MODEL_MAPPING[self.model.__name__])
            filter_fields = filter_model.objects.filter(
                place_type__in=place_types
            ).exclude(
                id__in=qs.values_list('field_type_id', flat=True)
            ).distinct()
            return filter_fields
        return None

    """A formset for child objects related to a parent."""

    def __init__(self, data=None, files=None, instance=None,
                 save_as_new=False, prefix=None, queryset=None, **kwargs):
        if instance is None:
            self.instance = self.fk.remote_field.model()
        else:
            self.instance = instance
        self.save_as_new = save_as_new
        if queryset is None:
            queryset = self.model._default_manager
        if self.instance.pk is not None:

            if self._get_extra_init(queryset, self.instance):
                # Populate kwargs with initial data so admin can see all available filter fields and
                # should just choose value for them.
                place_field_init = []
                for ff in self._get_extra_init(queryset, self.instance):
                    place_field_init.append({
                        'field_type': ff
                    })
                kwargs['initial'] = place_field_init

            qs = queryset.filter(**{self.fk.name: self.instance})

        else:
            qs = queryset.none()
        self.unique_fields = {self.fk.name}
        super(BaseInlineFormSet, self).__init__(data, files, prefix=prefix,
                                                queryset=qs, **kwargs)

        # Add the generated field to form._meta.fields if it's defined to make
        # sure validation isn't skipped on that field.
        if self.form._meta.fields and self.fk.name not in self.form._meta.fields:
            if isinstance(self.form._meta.fields, tuple):
                self.form._meta.fields = list(self.form._meta.fields)
            self.form._meta.fields.append(self.fk.name)


class PlaceFilterFieldInline(admin.TabularInline):
    template = 'admin/edit_inline/tabular_for_filter_fields.html'
    formset = FilterBaseInlineFormSet
    extra = 0
    max_num = 0
    obj = None

    def get_fields(self, request, obj=None):
        if self.fields:
            return self.fields
        # saved object to use it in self.formfield_for_foreignkey
        self.obj = obj
        form = self.get_formset(request, obj, fields=None).form
        return list(form.base_fields) + list(self.get_readonly_fields(request, obj))

    def get_extra(self, request, obj=None, **kwargs):
        '''
        In our inline for filter field (good_spot.filter.models.PlaceField) we want to see all available 
        filter fields (good_spot.filter.models.FilterField) for current place along with already existing. 
        Available field types depends on place types (good_spot.places.models.PlaceType) of current place
        and place types of filter fields. Here we count how many available filter fields and override `extra`
        '''
        if obj:
            # existing_filter_fields = obj.place_filter_fields.all()
            existing_filter_fields = self.model.objects.filter(place=obj)
            place_types = obj.place_types.all()
            # get filter fields available for this place types
            filter_model = apps.get_model('filter', filter_models.FILTER_MODEL_MAPPING[self.model.__name__])
            available_filter_fields = filter_model.objects.filter(
                place_type__in=place_types
            ).exclude(
                id__in=existing_filter_fields.values_list('field_type_id', flat=True)
            ).distinct()
            return available_filter_fields.count()
        return self.extra

    def get_max_num(self, request, obj=None, **kwargs):
        # We need this to hide `+ Add another` button
        if obj:
            filter_model = apps.get_model('filter', filter_models.FILTER_MODEL_MAPPING[self.model.__name__])
            return filter_model.objects.filter(
                place_type__in=obj.place_types.all()
            ).distinct().count()

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(PlaceFilterFieldInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
        # filter queryset for field_type by place.place_types
        if db_field.name == 'field_type' and self.obj:
            filter_model = apps.get_model('filter', filter_models.FILTER_MODEL_MAPPING[self.model.__name__])
            place_types_pks = filter_model.objects.filter(place_type__in=self.obj.place_types.all()).values_list(
                'place_type__pk', flat=True).distinct()
            field.queryset = filter_model.objects.filter(place_type__pk__in=place_types_pks).distinct()
        return field


class PlaceChoiceFilterFieldForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = self.fields['value'].queryset
        if self.initial.get('field_type'):
            field_type = self.initial.get('field_type')
            if isinstance(field_type, filter_models.ChoiceFilterField):
                self.fields['value'].queryset = queryset.filter(choice_filter_field=field_type)
            elif isinstance(field_type, int):
                self.fields['value'].queryset = queryset.filter(choice_filter_field_id=field_type)
            else:
                self.fields['value'].queryset = queryset


class PlaceChoiceFilterFieldInline(PlaceFilterFieldInline):
    model = filter_models.PlaceChoiceFilterField
    form = PlaceChoiceFilterFieldForm


class PlaceBoolFilterFieldInline(PlaceFilterFieldInline):
    model = filter_models.PlaceBoolFilterField


class PlaceTextFilterFieldInline(PlaceFilterFieldInline):
    model = filter_models.PlaceTextFilterField
