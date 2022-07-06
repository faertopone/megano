from django.db import models
from django.db.models import Manager, QuerySet, Sum
from django.utils.translation import gettext_lazy as _
from django.db.models import F

from products.models import Product
from accounts.models import Client


class BasketQuerySet(QuerySet):

    @property
    def total_price(self):
        """
        Сумма всех объектов корзины пользователя
        """
        r = self.annotate(
            total_price=Sum('price') * F('qty')
        ).aggregate(Sum('total_price'))['total_price__sum']
        return r if r is not None else 0

    @property
    def total_count(self):
        """
        Суммарное количество товаров всех объектов корзины
        """
        r = self.aggregate(Sum('qty'))['qty__sum']
        return r if r is not None else 0

    def my_update_or_create(self, defaults=None, **kwargs):
        """
        Создаем объект корзины в зависимости от того, залогинился юзер
        или нет
        """
        if kwargs['request'].user.is_authenticated:
            kwargs['client'] = kwargs.pop('request').user.client
        else:
            kwargs['session'] = kwargs.pop('request').session.session_key
        return super().update_or_create(defaults=defaults, **kwargs)

    def smart_filter(self, request):
        """
        Берем нужные объекты корзины в зависимости от того, залогинился юзер
        или нет
        """
        if request.user.is_authenticated:
            return self.filter(client=request.user.client)
        return self.filter(session=request.session.session_key)

    def get_item(self, request, product):
        """
        Берем нужный объект корзины в зависимости от того, залогинился юзер или
        нет
        """
        if request.user.is_authenticated:
            return self.get(client=request.user.client, product=product)
        return self.get(session=request.session.session_key, product=product)


class BasketManager(Manager):

    def get_queryset(self):
        return BasketQuerySet(self.model, using=self._db)

    @property
    def total_price(self):
        return self.get_queryset().total_price

    @property
    def total_count(self):
        return self.get_queryset().total_count

    def smart_filter(self, request):
        return self.get_queryset().smart_filter(request)

    def get_item(self, request, product):
        return self.get_queryset().get_item(request, product)

    def my_update_or_create(self, **kwargs):
        return self.get_queryset().my_update_or_create(**kwargs)


class BasketItem(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_('Продукт'),
        related_name='basket_items',
        null=True
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name=_('Клиент'),
        related_name='basket_items',
        null=True, blank=True
    )
    qty = models.PositiveSmallIntegerField(
        _("Количество"),
        default=1
    )
    price = models.DecimalField(
        _('Стоимость'),
        max_digits=9,
        decimal_places=2,
        default=0
    )
    session = models.CharField(
        max_length=256,
        verbose_name=_('Ключ сессии'),
        blank=True, null=True,
    )
    old_price = models.DecimalField(
        _('Стоимость без скидки'),
        max_digits=9,
        decimal_places=2,
        default=0
    )
    seller = models.CharField(
        max_length=100,
        verbose_name=_('Продавец'),
        blank=True
    )
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name='Последнее обновление'
    )
    objects = BasketManager()

    class Meta:
        verbose_name = 'Товар из корзины'
        verbose_name_plural = 'Товары из корзины'

    @property
    def total_price(self):
        return self.price * self.qty

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.qty == 0:
            return super(BasketItem, self).delete()
        return super(BasketItem, self).save()
