from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import os


class FixtureFile(models.Model):
    """
    Пока в разработке
    """
    file = models.FileField(upload_to='admin_fixtures', verbose_name=_('файл фикстур'))

    class Meta:
        verbose_name = _('файл фикстур')
        verbose_name_plural = _('файлы фикстур')

