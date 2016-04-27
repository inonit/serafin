from django.apps import AppConfig, apps


class SystemConfig(AppConfig):
    name = 'system'

    def ready(self):
        import system.signals
