import json

from braces.views import SuperuserRequiredMixin
from django.conf import settings
from django.template.loader import render_to_string
from django.views import generic

from good_spot.places import models as places_models
from good_spot.place_editor import serializers as place_editor_serializer
from good_spot.place_editor import schema_serializers as place_editor_schema_serializer
from good_spot.place_editor import schemas as place_editor_schemas

WEEKDAY_MAPPING = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}


class PlaceDetailView(SuperuserRequiredMixin, generic.DetailView):
    template_name = 'places/place_detail.html'
    model = places_models.Place

    def get_context_data(self, **kwargs):
        context = super(PlaceDetailView, self).get_context_data(**kwargs)
        serializer = place_editor_serializer.PlaceInitSchemaSerializer(instance=self.object)

        context['properties'] = place_editor_schema_serializer.PlaceGenerateEditSchema(instance=self.object).data
        context['initial'] = json.dumps(serializer.data)

        context['updating_rules_schema_items'] = place_editor_schemas.updating_rules_schema_items

        updating_rules_initial = []
        rules = self.object.get_rules()
        for rule in rules:
            updating_rules_initial.append({
                "day": rule.start.weekday(),
                "time": rule.start.strftime("%H:%M")
            })
        context['updating_rules_initial'] = updating_rules_initial

        context['updating_place_types_rules'] = self.object.get_place_types_rules()

        if self.object.populartimes:
            context['populartimes'] = render_to_string('places/populartimes.html', {
                'object': self.object.populartimes
            })
        else:
            context['populartimes'] = None

        return context


class PlaceCreateView(SuperuserRequiredMixin, generic.CreateView):
    template_name = 'places/place_form.html'
    model = places_models.Place
    fields = ['google_place_id', 'is_published', 'update_populartimes']

    def get_context_data(self, **kwargs):
        context = super(PlaceCreateView, self).get_context_data(**kwargs)
        context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY
        context['properties'] = place_editor_schemas.place_schema_add
        return context
