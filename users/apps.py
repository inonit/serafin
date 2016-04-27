from django.apps import AppConfig, apps


class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        import users.signals
