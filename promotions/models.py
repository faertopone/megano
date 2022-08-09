from django.db import models
from django.utils.translation import gettext_lazy as _


class Promotions(models.Model):
    """
    Модель акций, которые определяют скидки на группы товаров, на общие покупки в магазинах.
    discount определяет процентную скидку 80% = 0.80
    Настройка параметров на товар дня
    """
    name = models.CharField(max_length=39, verbose_name=_('название'))
    description = models.TextField(max_length=500, blank=True, default="", verbose_name=_('описание'))
    discount = models.FloatField(verbose_name=_('скидка, %'), default=0)

    class Meta:
        verbose_name = _('скидка')
        verbose_name_plural = _('скидки')

    def __str__(self):
        return self.name


class PromotionsShowProduct(models.Model):
    """
    Модель товара дня на главной странице, и сколько дней он там будет.
    """

    limit_day_show_product = models.PositiveSmallIntegerField(verbose_name=_('Сколько дней показывать товар дня'),
                                                              default=1, blank=True)
    product_show = models.ForeignKey("products.Product", on_delete=models.CASCADE,
                                     verbose_name=_("товар дня"),
                                     help_text=_('выберите товар, который будет показан как товар дня'), null=True,
                                     blank=True)

    def __str__(self):
        return 'Товар дня - настройка'

    class Meta:
        verbose_name = _("Товар дня - настройка")
        verbose_name_plural = _("Товары дня - настройка")


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
