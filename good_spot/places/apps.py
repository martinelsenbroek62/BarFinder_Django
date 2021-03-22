from django.apps import AppConfig


class PlacesConfig(AppConfig):
    name = 'good_spot.places'

    def ready(self):
        from good_spot.places import signals
