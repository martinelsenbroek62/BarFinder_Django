from django.apps import AppConfig


class ReportConfig(AppConfig):
    name = 'good_spot.report'

    def ready(self):
        from .receivers import notify_admins_on_new_feedback
