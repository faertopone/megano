from django.db.models import Sum, F, DecimalField, FloatField, Max
from django.http import HttpRequest
from accounts.models import Client
from basket.models import BasketItem
from orders.models import OrderProductBasket


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


def order_service(order, user: HttpRequest) -> None:
    """
    Функция добавляет номер заказу и добавляет заказ к этому клиенту
    """
    client = Client.objects.select_related('user').prefetch_related('item_view', 'orders').get(user=user)
    basket = BasketItem.objects.filter(client=client)
    # ================= ТУТ ЗНАЧЕНИЯ ИЗ МОДЕЛИ СКИДОК
    price_delivery = 500
    freed_delivery = 200
    if basket.exists():
        for item in basket:
            data = {'product': item.product,
                    'count': item.qty,
                    'seller': '',
                    'price': item.price,
                    'old_price': ''
                    }
            order_item = OrderProductBasket.objects.create(**data)
            order.order_products.add(order_item)
    if client.orders.all():
        order.number_order = len(client.orders.all())
    client.full_address = order.address
    client.city = order.city
    total_basket = basket.aggregate(price_sum=Sum(F('price') * F('qty')))
    order.total_price = total_basket.get('price_sum')
    # тут еще добавить условие про разных продавцом (если продукты из разных магазинов)
    if order.total_price <= 2000:
        order.total_price += freed_delivery
    if order.delivery == 'Экспресс доставка':
        order.total_price += price_delivery
    # Привяжем заказ к текущем клиенту
    order.save()
    client.save()
    basket.delete()
    client.orders.add(order)
