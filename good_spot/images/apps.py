from django.apps import AppConfig


class ImagesConfig(AppConfig):
    name = 'good_spot.images'

    def ready(self):
        from good_spot.images import signals
