from __future__ import absolute_import, unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


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
