from django.db import models
from django.utils.translation import gettext_lazy as _


class Order(models.Model):
    """
    Модель заказа товаров
    """
    CHOICES_DELIVERY = [('Обычная доставка', _('Обычная доставка')),
                        ('Экспресс доставка', _('Экспресс доставка'))]

    CHOICES_PAY = [('Онлайн картой', _('Онлайн картой')),
                   ('Онлайн со случайного чужого счета', _('Онлайн со случайного чужого счета')),]

    created_dt = models.DateField(auto_now_add=True)
    products_items = models.ManyToManyField('ProductBasket', verbose_name=_('Товары для заказа'))
    first_name = models.CharField(max_length=20, default='', verbose_name=_('Имя'))
    last_name = models.CharField(max_length=20, default='', verbose_name=_('Фамилия'))
    patronymic = models.CharField(default='', max_length=20,
                                  error_messages={'max_length': 'Слишком длинное Отчество!'},
                                  verbose_name=_('Отчество'))

    delivery = models.CharField(max_length=50, choices=CHOICES_DELIVERY, db_index=True,
                                verbose_name=_('Способ доставки'), default='Обычная доставка')
    city = models.CharField(max_length=30, default='', verbose_name=_('Город'))
    address = models.TextField(verbose_name=_('Адрес'), default='')
    payment = models.CharField(max_length=50, choices=CHOICES_PAY, db_index=True, verbose_name=_('Способ оплаты'),
                               default='Онлайн картой')
    total_price = models.DecimalField(verbose_name=_("Сумма заказа"),
                                      max_digits=9,
                                      decimal_places=2,
                                      default=0)
    status_pay = models.BooleanField(default=False, verbose_name=_('Статус оплаты'))
    error_pay = models.CharField(max_length=300, verbose_name=_('Ошибки, если оплата не прошла'), null=True)
    transaction = models.PositiveBigIntegerField(verbose_name=_('Номер транзакции оплаты'), unique=True, null=True)

    def __str__(self):
        return _('Заказ_') + str(self.id)

    class Meta:
        verbose_name = _('заказ')
        verbose_name_plural = _('заказы')
        db_table = 'Orders'
        ordering = ['-created_dt']


class ProductBasket(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE,
                                related_name='client_products_order',
                                related_query_name='client_products_orders')
    count = models.IntegerField(default=1, verbose_name=_('Сколько товара'))
    seller = models.CharField(max_length=100, verbose_name=_('Продавец'))
    created_dt = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ("-created_dt",)
