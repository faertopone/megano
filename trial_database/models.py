"""
Пробная база данных, сделал по второму варианту из схемы.
Миграции не делал. Здесь есть Gettext
"""

from __future__ import absolute_import, unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class UserProfile(models.Model):
    """
    Модель  данных о пользователе (адрес, телефон, дата рождения, статус),
    дополняющая модель User
    """
    STATUS_CHOICES = [
        ('a', 'status_1'), ('b', 'status_2'), ('c', 'status_3'), ('d', 'status_4')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('user'))
    city = models.CharField(max_length=39, blank=True, verbose_name=_('city'))
    street = models.CharField(max_length=50, blank=True, verbose_name=_('street'))
    postcode = models.IntegerField(verbose_name=_('postcode'), default=0)
    house_number = models.IntegerField(verbose_name=_('house_number'), default=0)
    apartment_number = models.IntegerField(verbose_name=_('apartment_number'), default=0)
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_('data of birth'))
    phone = models.CharField(null=True, max_length=15, blank=True, verbose_name=_('phone'))
    full_sum_spending = models.IntegerField(verbose_name=_('full sum spending'), default=0)
    photo = models.ImageField(upload_to='user_photo', default='default.jpg')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='a', verbose_name=_('status'))

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('users profile')

    def __str__(self):
        return self.user.name


class Promotions(models.Model):
    """
    Модель акций, которые определяют скидки на группы товаров, на общие покупки в магазинах.
    discount щпределяет процентную скидку 80% = 0.80
    """
    name = models.CharField(max_length=39, blank=True, verbose_name=_('name'))
    description = models.TextField(max_length=500, blank=True, verbose_name=_('description'))
    discount = models.FloatField(verbose_name=_('discount'), default=0)  # скидка

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
    name = models.CharField(max_length=39, blank=True, verbose_name=_('name'))
    description = models.TextField(max_length=500, blank=True, verbose_name=_('description'))
    city = models.CharField(max_length=39, blank=True, verbose_name=_('city'))
    street = models.CharField(max_length=50, blank=True, verbose_name=_('street'))
    house_number = models.IntegerField(verbose_name=_('house number'), default=0)
    phone = models.CharField(null=True, max_length=15, blank=True, verbose_name=_('phone'))
    email = models.EmailField(null=True, max_length=256, blank=True, verbose_name='email')
    rating = models.IntegerField(verbose_name=_('rating'), default=0)
    promotion = models.ForeignKey(Promotions, on_delete=models.CASCADE, verbose_name=_('promotion'))

    class Meta:
        verbose_name = _('shop')
        verbose_name_plural = _('shops')

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Модель содержит характеристики категорий товаров,
    activity определяет участие определенной категории в акциях.
    """
    STATUS_CHOICES = [
        ('y', _('current')),
        ('n', _('inactive'))
    ]
    name = models.CharField(max_length=250, verbose_name=_('category name'))
    icon_field = models.ImageField(upload_to='category_icon', default='default.jpg', verbose_name=_('icon'))
    description = models.TextField(max_length=500, blank=True, verbose_name=_('description'))
    activity = models.CharField(max_length=1, choices=STATUS_CHOICES, default='n', verbose_name=_('activity'))

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return self.name


class Properties(models.Model):
    """
    Модель, связывающая определённые характеристики (свойства) товара c категорией
    (телевизор: диагональ, экран;
    пылесос: мощность, габариты...)
    """

    name = models.CharField(max_length=250, verbose_name=_('name'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('category'))

    class Meta:
        verbose_name = _('property')
        verbose_name_plural = _('properties')

    def __str__(self):
        return self.name


class Group(models.Model):
    """
    Модель, связывающая группы товаров с определёнными акциями
    """

    number = models.IntegerField(verbose_name=_('number group'), default=0)
    promotion = models.ForeignKey(Promotions, on_delete=models.CASCADE, verbose_name=_('promotion'))


class Products(models.Model):
    """
    Модель профиля товара. Содержит подробную информацию о товаре,
    связывает его с категорией товара и определяет номер группы для участия в акциях.
    """
    STATUS_CHOICES = [
                ('y', _('current')),
                ('n', _('inactive'))
            ]
    article = models.CharField(max_length=25, default='NOTARTICLE', blank=True, verbose_name=_('article'))
    name = models.CharField(max_length=39, blank=True, verbose_name=_('name'))
    price = models.DecimalField(verbose_name=_('price'), decimal_places=2, default=0)
    rating = models.IntegerField(verbose_name=_('rating'), default=0)
    flag_limit = models.CharField(max_length=1, choices=STATUS_CHOICES, default='n', verbose_name=_('limit status'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('category'))
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name=_('group'))

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')

    def save(self, *args, **kwargs):
        self.article = str(self.pk) + '-' + str(self.name) + '-' + str(self.category) + '-' + str(self.group)
        super(Products, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class PropertiesProduct(models.Model):
    """
    Модель, связывающая конкретный товар с его характеристиками
    """
    property = models.ForeignKey(Properties, on_delete=models.CASCADE, verbose_name=_('properties'))
    product = models.ForeignKey(Products, on_delete=models.CASCADE, verbose_name=_('product'))
    value = models.TextField(max_length=500, blank=True, verbose_name=_('value of Property'))

    class Meta:
        verbose_name = _('product property')
        verbose_name_plural = _('products properties')

    def __str__(self):
        return self.value


class ProductPhoto(models.Model):
    """
    Модель с фотографиями товаров
    """
    photo = models.ImageField(upload_to='product_photo', default='default.jpg', verbose_name=_('product photo'))
    product = models.ForeignKey(Products, on_delete=models.CASCADE, verbose_name=_('product'))

    class Meta:
        verbose_name = _('products photo')
        verbose_name_plural = _('products Photo')


class ShopPhoto(models.Model):
    """
    Модель с фотографиями магазинов
    """
    photo = models.ImageField(upload_to='shops_photo', default='default.jpg', verbose_name=_('shops_photo'))
    shop = models.ForeignKey(Shops, on_delete=models.CASCADE, verbose_name=_('shop'))

    class Meta:
        verbose_name = _('shops photo')
        verbose_name_plural = _('shops photos')


class ShopProduct(models.Model):
    """
    Модель, связывающая товар с магазином,
    определяет количество товара в магазине, цену в конкретном магазине
    """
    shop = models.ForeignKey(Shops, on_delete=models.CASCADE, verbose_name=_('shops'))
    product = models.ForeignKey(Products, on_delete=models.CASCADE, verbose_name=_('product'))
    amount = models.IntegerField(verbose_name=_('amount'), default=0)
    price_in_shop = price = models.DecimalField(verbose_name=_('price'), decimal_places=2, default=0)
    promotion = models.ForeignKey(Promotions, on_delete=models.CASCADE, verbose_name=_('promotion'))
    special_price = models.FloatField(verbose_name=_('special price'), default=0)

    class Meta:
        verbose_name = _('product in shop')
        verbose_name_plural = _('products in shop')

    def __str__(self):
        return self.product.name


class Basket(models.Model):
    """
    Корзина товаров, выбранных пользователем для оплаты и оформления заказа.
    После оплаты товар приобретает статус «оплаченный».
    Статус доставки определяется после полной обработки заказа.
    """
    STATUS_PAID_CHOICES = [
        ('y', _('item paid')),
        ('n', _('item not paid'))
    ]
    STATUS_READY_CHOICES = [
        ('y', _('item ready')),
        ('n', _('item not ready'))
    ]
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name=_('profile'))
    shop_product = models.ForeignKey(ShopProduct, on_delete=models.CASCADE, verbose_name=_('product in shop'))
    amount = models.IntegerField(verbose_name=_('amount'), default=0)
    selection_time = models.DateTimeField(verbose_name='selection_time', auto_now_add=True)
    status_paid = models.CharField(max_length=1, choices=STATUS_PAID_CHOICES,
                                   default='n', verbose_name=_('status paid'))
    status_ready = models.CharField(max_length=1, choices=STATUS_READY_CHOICES, default='n',
                                    verbose_name=_('status ready'))

    class Meta:
        verbose_name = _('product in user basket')
        verbose_name_plural = _('products in user basket')

    def __str__(self):
        return self.shop_product.name


class Banners(models.Model):
    """
    Модель баннеров, которые используются для рекламы на сайте
    """
    photo = models.ImageField(upload_to='banners_photo', default='default.jpg', verbose_name=_('banner photo'))
    description = models.TextField(max_length=500, blank=True, verbose_name=_('description'))
    creation_date = models.DateTimeField(verbose_name='selection_time', auto_now_add=True)
