from django.apps import AppConfig


class AppWebshopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_webshop'

    # Обязательно, чтобы работали сигналы
    def ready(self):
        import app_webshop.signals  # noqa: F401
