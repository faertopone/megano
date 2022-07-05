from django.core.validators import RegexValidator
from django.db import models
from django.forms import RadioSelect
from django.utils.translation import gettext_lazy as _

from accounts.models import Client


class Order(models.Model):
    """
    Модель заказа товаров
    """
    CHOICES_DELIVERY = [('Обычная доставка', _('Обычная доставка')),
                        ('Экспресс доставка', _('Экспресс доставка'))]

    CHOICES_PAY = [('Онлайн картой', _('Онлайн картой')),
                   ('Онлайн со случайного чужого счета', _('Онлайн со случайного чужого счета')), ]

    created_dt = models.DateField(auto_now_add=True)
    order_products = models.ManyToManyField('OrderProductBasket', verbose_name=_('товары для заказа'),
                                            related_name='order_products')
    first_name = models.CharField(max_length=20, default='', verbose_name=_('Имя'))
    last_name = models.CharField(max_length=20, default='', verbose_name=_('Фамилия'))
    patronymic = models.CharField(default='', max_length=20,
                                  error_messages={'max_length': 'Слишком длинное Отчество!'},
                                  verbose_name=_('Отчество'))

    delivery = models.CharField(max_length=50, choices=CHOICES_DELIVERY, db_index=True,  default='Обычная доставка',
                                verbose_name=_('Способ доставки'))
    city = models.CharField(max_length=30, default='', verbose_name=_('Город'))
    address = models.TextField(verbose_name=_('Адрес'), default='')
    payment = models.CharField(max_length=50, choices=CHOICES_PAY, db_index=True, verbose_name=_('Способ оплаты'),
                               default='Онлайн картой')
    total_price = models.DecimalField(verbose_name=_("Сумма заказа"),
                                      max_digits=9,
                                      decimal_places=2,
                                      default=0)
    status_pay = models.BooleanField(default=False, verbose_name=_('Статус оплаты'))
    need_pay = models.BooleanField(default=False, verbose_name=_('Флаг, что нужно поставить в очередь на оплату'))
    error_pay = models.CharField(max_length=300, verbose_name=_('Ошибки, если оплата не прошла'), null=True)
    transaction = models.PositiveBigIntegerField(verbose_name=_('Номер транзакции оплаты'), unique=True, null=True)
    number_visa = models.PositiveBigIntegerField(verbose_name=_('Номер карты оплаты'), null=True)
    number_order = models.IntegerField(verbose_name=_('Номер заказа'), default=1)
    email = models.EmailField(verbose_name=_('email'))
    phoneNumberRegex = RegexValidator(
        regex=r"^\+?7?\d{8,15}$",
        message='Введите корректный номер, без пробелов (+79999999999)'
    )
    phone = models.CharField(null=True,
                             verbose_name=_('контактный номер'),
                             validators=[phoneNumberRegex],
                             max_length=16,
                             )


    def __str__(self):
        return _('Заказ_') + str(self.number_order)

    class Meta:
        verbose_name = _('заказ')
        verbose_name_plural = _('заказы')
        db_table = 'Orders'
        ordering = ['-number_order']


class OrderProductBasket(models.Model):
    """
    Модель одного продукта товара в корзине с параметрами
    """
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT,
                                related_name='order_product',
                                related_query_name='client_products_basket')
    count = models.IntegerField(default=1, verbose_name=_('Сколько товара'))
    seller = models.CharField(max_length=100, verbose_name=_('Продавец'))
    created_dt = models.DateField(auto_now_add=True)
    price = models.DecimalField(
        _('Стоимость после скидки'),
        max_digits=9,
        decimal_places=2,
    )
    old_price = models.DecimalField(
        _('Стоимость '),
        max_digits=9,
        decimal_places=2,
    )

    class Meta:
        ordering = ("-created_dt",)
