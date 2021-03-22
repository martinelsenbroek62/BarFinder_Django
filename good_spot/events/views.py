import random
from constance import config
from django.shortcuts import redirect
from django.views import generic
from good_spot.places import models as places_models
from good_spot.proxy import models as proxy_models

COLOR_MAPPING = {
    'bar': '#B10B52',
    'restaurant': '#F7981C',
    'night_club': '#53C7E9',
    'karaoke': '#7C30FE'
}
r = lambda: random.randint(0, 255)


class EventSchedule(generic.TemplateView):
    template_name = 'events/schedule.html'

    def get(self, request, *args, **kwargs):
        # todo add permissions instead
        if not request.user or not request.user.is_authenticated() or not request.user.is_superuser:
            return redirect('/admin/')
        return super(EventSchedule, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EventSchedule, self).get_context_data(**kwargs)

        qs_cities = places_models.City.objects.all()
        active_place_types = places_models.PlaceType.objects.filter(
            is_active=True
        ).prefetch_related('active_in_cities')

        qs_places_all = places_models.Place.active_objects.all()
        active_places_pks = list(set(qs_places_all.values_list('pk', flat=True)))
        qs_places = places_models.Place.objects.filter(
            pk__in=active_places_pks
        ).select_related(
            'city'
        ).prefetch_related(
            'place_types'
        )

        datasets = []

        for pt in active_place_types:
            dataset = {}
            dataset['label'] = pt.name

            hex_color = '#{:02x}{:02x}{:02x}'.format(r(), r(), r())  # generation of random HEX color
            dataset['backgroundColor'] = COLOR_MAPPING[pt.slug] if COLOR_MAPPING.get(pt.slug, None) else hex_color

            data_by_cities = []
            for city in qs_cities:
                if city.is_active and city in pt.active_in_cities.all():
                    data_by_cities.append(qs_places.filter(
                        place_types__id=pt.id,
                        city_id=city.id
                    ).count())
                else:
                    data_by_cities.append(0)

            dataset['data'] = data_by_cities
            datasets.append(dataset)

        context['datasets'] = datasets
        context['stat_cities'] = list(qs_cities.values_list('name', flat=True))
        context['places_count'] = qs_places.count()
        context['proxies_count'] = proxy_models.Proxy.objects.count()
        context['recommended_updates_count'] = int(60 / config.DELAY_BETWEEN_PROXY_REQUESTS_IN_MINUTES
                                                   * proxy_models.Proxy.objects.count())
        context['updates_switched_on'] = config.UPDATE_PLACES_HOURLY
        return context
