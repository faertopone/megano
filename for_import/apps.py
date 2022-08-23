from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FileFixtureConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "for_import"
    verbose_name = _("файлы фикстур")
