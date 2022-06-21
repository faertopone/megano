from __future__ import absolute_import, unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from products.models import Product, ProductPhoto


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


class Shops(models.Model):
    """
    Модель профиля магазина. Содержит подробную информацию о продавце
    (название, описание, адрес, рейтинг, участие в акциях).
    """
    name = models.CharField(max_length=39, verbose_name=_('название'))
    description = models.TextField(max_length=500, blank=True, default="", verbose_name=_('описание'))
    city = models.CharField(max_length=39, verbose_name=_('город'))
    street = models.CharField(max_length=50, verbose_name=_('улица'))
    house_number = models.IntegerField(verbose_name=_('номер дома'), default=0)
    phone = models.CharField(max_length=15, verbose_name=_('телефон'))
    email = models.EmailField(max_length=256, verbose_name='email')
    rating = models.IntegerField(verbose_name=_('рэйтинг'), default=0)
    promotion = models.ForeignKey(Promotions, on_delete=models.CASCADE, verbose_name=_('скидка'))
    # shop_photo = models.ManyToManyField("ShopPhoto")
    # shop_product = models.ManyToManyField("ShopProduct")

    class Meta:
        verbose_name = _('магазин')
        verbose_name_plural = _('магазины')

    def __str__(self):
        return self.name


class ShopPhoto(models.Model):
    """
    Модель с фотографиями магазинов
    """
    photo = models.ImageField(upload_to='shops_photo', default='default.jpg', verbose_name=_('фото'))
    shop = models.ForeignKey(Shops, on_delete=models.CASCADE, verbose_name=_('магазин'))

    class Meta:
        verbose_name = _('фото магазина')
        verbose_name_plural = _('фото магазина')


class ShopUser(models.Model):
    """
    Модель, связывающая пользователя с магазином.
    У пользователя открыты права для редактирования профиля магазина,
    редактирования товаров в магазине.
    """
    shop = models.ForeignKey(Shops, on_delete=models.CASCADE, verbose_name=_('магазин'))
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('продавец'))


class ShopProduct(models.Model):
    """
    Модель, связывающая товар с магазином,
    определяет количество товара в магазине, цену в конкретном магазине
    """
    shop = models.ForeignKey(Shops, on_delete=models.CASCADE, verbose_name=_('магазин'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('товар'),
                                related_name="shop_product", related_query_name="shop_product")
    amount = models.IntegerField(verbose_name=_('количество'), default=0)
    price_in_shop = models.DecimalField(verbose_name=_('цена'), decimal_places=2, max_digits=10, default=0)
    promotion = models.ForeignKey(Promotions, on_delete=models.CASCADE, verbose_name=_('скидка'))
    special_price = models.DecimalField(verbose_name=_('спец-цена'), decimal_places=2, max_digits=10, default=0)
    photo_url = models.TextField(max_length=500, blank=True, default="", verbose_name=_('ссылка на фото'))
    sale = models.IntegerField(verbose_name=_('sale'), default=0)

    def save(self, *args, **kwargs):
        try:
            self.photo_url = ProductPhoto.objects.filter(product=self.product)[0].photo.url
        except Exception:
            pass
        self.special_price = self.price_in_shop * (100 - self.sale)/100
        super(ShopProduct, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('товар в магазине')
        verbose_name_plural = _('товары в магазине')

    def __str__(self):
        return self.product.name
