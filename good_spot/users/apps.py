from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'good_spot.users'

    def ready(self):
        from good_spot.users import signals
