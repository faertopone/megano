"""
Пробная база данных, сделал по второму варианту из схемы.
Миграции не делал. Здесь есть Gettext
"""

from __future__ import absolute_import, unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator


def banners_directory_path(instance, filename):
    # путь, куда будет осуществлена загрузка MEDIA_FILES/banners_photo/name_баннера + <filename>
    return 'banners_photo/{name}_photo_+{filename}'.format(name=instance.name, filename=filename)

class Banners(models.Model):
    """
    Модель баннеров, которые используются для рекламы на сайте
    """
    name = models.CharField(max_length=15, verbose_name=_('название баннера'))
    name_product = models.CharField(max_length=40, verbose_name=_('название товара'), null=True)
    photo = models.ImageField(upload_to=banners_directory_path, null=True, verbose_name=_('Фотография для баннера'))
    url_link = models.CharField(max_length=300, verbose_name=_('url на товар'), default='')
    description = models.TextField(blank=True, verbose_name=_('описание'))
    is_active = models.BooleanField(default=True, verbose_name=_('статус активности'))
    creation_date = models.DateTimeField(verbose_name='дата создания', auto_now_add=True)
    version = models.CharField(max_length=10, verbose_name=_('Серия/версия продукта'), null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Banners'
        verbose_name = _('Баннер')
        verbose_name_plural = _('Баннеры')