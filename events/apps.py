from django.apps import AppConfig, apps


class EventsConfig(AppConfig):
    name = 'events'

    def ready(self):
        import events.signals
