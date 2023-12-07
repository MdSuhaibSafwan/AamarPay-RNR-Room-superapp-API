from django.apps import AppConfig


class RNRConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rnr'

    def ready(self):
        from . import signals
