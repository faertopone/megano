from django.db import models
from django.utils.translation import gettext_lazy as _


class FixtureFile(models.Model):
    """
    Пока в разработке
    """
    STATUS_CHOICES = [
        ('y', _('processed')),
        ('n', _('not processed'))
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='n', verbose_name=_('статус'))
    name = models.CharField(max_length=1000, verbose_name=_("название фстуры"), default='NON')
    file = models.FileField(upload_to='admin_fixtures', verbose_name=_('файл фикстур'))
    extension = models.CharField(max_length=10, verbose_name=_("расширение файла"), default='NON')
    priority = models.IntegerField(verbose_name=_("очередность"), default=0)

    class Meta:
        verbose_name = _('файл фикстур')
        verbose_name_plural = _('файлы фикстур')

    def save(self, *args, **kwargs):
        self.name = str(self.file).split('.')[0]
        self.extension = str(self.file).split('.')[1]

        name_dict = {'category': 3, 'product': 4, 'property': 5, 'property_category': 7, 'property_product': 6,
                     'promotions': 1, 'promotion_group': 2, 'banners': 8, 'client': 9, 'shop': 10, 'shop_photo': 11,
                     'shop_product': 12, 'interval': 13, 'clearing_basket': 14}
        for key, value in name_dict.items():
            if key == str(self.file).split('.')[0]:
                self.name = key
                self.priority = value
        super().save(*args, **kwargs)
