from django.db import models
from django.utils.translation import gettext_lazy as _

from products.models import Product
from accounts.models import Client


class BasketItem(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_('Продукт'),
        related_name='basket_items'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name=_('Клиент'),
        related_name='basket_items',
    )
    qty = models.PositiveSmallIntegerField(
        _("Количество"),
    )
    price = models.DecimalField(
        _('Стоимость'),
        max_digits=9,
        decimal_places=2,
    )
