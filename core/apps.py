from django.apps import AppConfig

class CoreConfig(AppConfig):
    name = 'core'  # your app name

    def ready(self):
        import core.signals  # replace 'core' with your app name
