from django.apps import AppConfig, apps


class TaskerConfig(AppConfig):
    name = 'tasker'

    def ready(self):
        import tasker.signals
