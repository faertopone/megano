from django.db import models
from django.utils.translation import gettext_lazy as _


class Promotions(models.Model):
    """
    Модель акций, которые определяют скидки на группы товаров, на общие покупки в магазинах.
    discount определяет процентную скидку 80% = 0.80
    """
    name = models.CharField(max_length=39, verbose_name=_('название'))
    description = models.TextField(max_length=500, blank=True, default="", verbose_name=_('описание'))
    discount = models.FloatField(verbose_name=_('скидка, %'), default=0)

    class Meta:
        verbose_name = _('скидка')
        verbose_name_plural = _('скидки')

    def __str__(self):
        return self.name


class PromotionGroup(models.Model):
    """
    Модель группы товаров, на каждый из которых действует
    указанная скидка.
    """
    name = models.CharField(max_length=200, verbose_name=_("название группы"))
    promotion = models.ForeignKey(Promotions, on_delete=models.CASCADE,
                                  related_name="promotion_groups", related_query_name="promotion_group",
                                  verbose_name=_("скидка"))

    class Meta:
        verbose_name = _("группа товаров со скидкой")
        verbose_name_plural = _("группы товаров со скидкой")

    def __str__(self):
        return self.name
