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
    name = models.CharField(max_length=39, verbose_name=_('name'))
    description = models.TextField(max_length=500, blank=True, verbose_name=_('description'))
    discount = models.FloatField(verbose_name=_('discount'), default=0)

    class Meta:
        verbose_name = _('promotion')
        verbose_name_plural = _('promotions')

    def __str__(self):
        return self.name


class Shops(models.Model):
    """
    Модель профиля магазина. Содержит подробную информацию о продавце
    (название, описание, адрес, рейтинг, участие в акциях).
    """
    name = models.CharField(max_length=39, verbose_name=_('name'))
    description = models.TextField(max_length=500, blank=True, verbose_name=_('description'))
    city = models.CharField(max_length=39, verbose_name=_('city'))
    street = models.CharField(max_length=50, verbose_name=_('street'))
    house_number = models.IntegerField(verbose_name=_('house number'), default=0)
    phone = models.CharField(max_length=15, verbose_name=_('phone'))
    email = models.EmailField( max_length=256, verbose_name='email')
    rating = models.IntegerField(verbose_name=_('rating'), default=0)
    promotion = models.ForeignKey(Promotions, on_delete=models.CASCADE, verbose_name=_('promotion'))
    # shop_photo = models.ManyToManyField("ShopPhoto")
    # shop_product = models.ManyToManyField("ShopProduct")

    class Meta:
        verbose_name = _('shop')
        verbose_name_plural = _('shops')

    def __str__(self):
        return self.name


class ShopPhoto(models.Model):
    """
    Модель с фотографиями магазинов
    """
    photo = models.ImageField(upload_to='shops_photo', default='default.jpg', verbose_name=_('shops_photo'))
    shop = models.ForeignKey(Shops, on_delete=models.CASCADE, verbose_name=_('shop'))

    class Meta:
        verbose_name = _('shops photo')
        verbose_name_plural = _('shops photos')


class ShopUser(models.Model):
    """
    Модель, связывающая пользователя с магазином.
    У пользователя открыты права для редактирования профиля магазина,
    редактирования товаров в магазине.
    """
    shop = models.ForeignKey(Shops, on_delete=models.CASCADE, verbose_name=_('shop'))
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('user'))


class ShopProduct(models.Model):
    """
    Модель, связывающая товар с магазином,
    определяет количество товара в магазине, цену в конкретном магазине
    """
    shop = models.ForeignKey(Shops, on_delete=models.CASCADE, verbose_name=_('shops'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('product'))
    amount = models.IntegerField(verbose_name=_('amount'), default=0)
    price_in_shop = models.DecimalField(verbose_name=_('price'), decimal_places=2, max_digits=10, default=0)
    promotion = models.ForeignKey(Promotions, on_delete=models.CASCADE, verbose_name=_('promotion'))
    special_price = models.DecimalField(verbose_name=_('special price'), decimal_places=2, max_digits=10, default=0)
    photo_url = models.TextField(max_length=500, blank=True, verbose_name=_('photo_url'))
    sale = models.IntegerField(verbose_name=_('sale'), default=0)

    def save(self, *args, **kwargs):
        try:
            self.photo_url = ProductPhoto.objects.filter(product=self.product)[0].photo.url
        except:
            pass
        self.special_price = self.price_in_shop * (100 - self.sale)/100
        super(ShopProduct, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('product in shop')
        verbose_name_plural = _('products in shop')

    def __str__(self):
        return self.product.name

