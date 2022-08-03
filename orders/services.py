from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from django.db import transaction
from django.http import HttpRequest
from accounts.models import Client
from basket.models import BasketItem
from orders.models import OrderProductBasket, OrderCopyProduct, DeliverySetting, Order


@transaction.atomic
def pay_order(id_order: int, visa_number: int):
    """
    Ставим в очередь ТАКС на оплату. Если номер карты четный значит оплачено, иначе ошибка
    """

    order = Order.objects.get(id=id_order)
    if visa_number % 2 == 0:
        # Имитация оплаты заказа
        order.status_pay = True
        order.transaction = f'{(visa_number // 6) * 3}'
        order.number_visa = visa_number
        order.error_pay = None
    else:
        order.status_pay = False
        order.error_pay = f'Карта с №{str(visa_number)} - не действительна!'

    order.need_pay = False
    order.save()


@dataclass
class OrderService:
    """
    Бизнес логика сервиса при оформлении заказа пользователем
    """
    basket: Any = None
    total_basket_price: Decimal = 0
    client: Any = None
    new_order_id: int = 0

    @staticmethod
    def get_limit_price_free() -> int:
        if DeliverySetting.objects.filter(is_active=True).first():
            return DeliverySetting.objects.filter(is_active=True).first().limit_price_free
        return 0

    @staticmethod
    def get_express_delivery_price() -> int:
        if DeliverySetting.objects.filter(is_active=True).first():
            return DeliverySetting.objects.filter(is_active=True).first().express_delivery_price
        return 0

    @staticmethod
    def get_delivery_price() -> int:
        if DeliverySetting.objects.filter(is_active=True).first():
            return DeliverySetting.objects.filter(is_active=True).first().delivery_price
        return 0

    def check_basket(self, request: HttpRequest):
        """
        Проверка корзины.
        """
        client = Client.objects.select_related('user').prefetch_related('item_view', 'orders').get(
            user=request.user)
        basket = BasketItem.objects.filter(client=client)
        self.basket = basket
        self.total_basket_price = basket.total_price
        self.client = client

    def check_free_delivery(self):
        """
        Проверка на условие на бесплатную доставку True - значит бесплатно.
        Если в корзине есть товары от разных продавцов, то доставка платная возвращает False
        """
        basket = self.basket
        seller = None
        for item in basket:
            if not seller:
                seller = item.shop
            else:
                if item.shop != seller:
                    return False

        if self.total_basket_price < self.get_limit_price_free():
            return False
        return True

    def order_copy_data(self, order: Order) -> None:
        """
              Функция добавляет номер заказу и добавляет заказ к этому клиенту
        """
        client = self.client
        basket = self.basket
        if basket:
            for item in basket:
                order_product_copy = OrderCopyProduct.objects.create(
                    product_pk=item.product.pk,
                    name=item.product.name,
                    description=item.product.description,
                    price=item.product.price,
                    photo=item.product.product_photo.first().photo
                )

                data = {'product': order_product_copy,
                        'count': item.qty,
                        'seller': item.shop,
                        'price': item.price,
                        'old_price': 0,
                        }
                order_item = OrderProductBasket.objects.create(**data)
                order.order_products.add(order_item)

        if client.orders.all():
            order.number_order = len(client.orders.all())
        client.full_address = order.address
        client.city = order.city
        if self.check_free_delivery():
            order.total_price = basket.total_price
        else:
            order.total_price = basket.total_price + self.get_delivery_price()
            order.delivery_price += self.get_delivery_price()

        if order.delivery == 'Экспресс доставка':
            order.total_price += self.get_express_delivery_price()
            order.delivery_price += self.get_express_delivery_price()
        order.save()
        client.save()
        basket.delete()
        client.orders.add(order)
        self.new_order_id = order.id


def initial_order_form(request: HttpRequest) -> dict:
    """
    Функция инициализирует начальные значения Профиля
    """
    client = Client.objects.select_related('user').prefetch_related('item_view').get(user=request.user)

    initial_client = {
        'phone': client.phone,
        'patronymic': client.patronymic,
        'first_name': client.user.first_name,
        'last_name': client.user.last_name,
        'email': client.user.email,
        'city': client.city,
        'address': client.full_address
    }
    return initial_client
