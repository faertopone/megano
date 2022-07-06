from django.core.files.images import ImageFile
from django.http import HttpRequest
from accounts.models import Client
from basket.models import BasketItem
from orders.models import OrderProductBasket, OrderCopyProduct


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


def calculation_delivery(total_price, item_in_basket):
    """
    Дополнительная стоимость на доставку
    """
    # ТУТ будет модель админа с настрйоками
    ORDER_SETTING_PRICE = 20000

    if total_price.real < ORDER_SETTING_PRICE:
        return 200
    return 0

def order_service(order, user: HttpRequest) -> None:
    """
    Функция добавляет номер заказу и добавляет заказ к этому клиенту
    """
    client = Client.objects.select_related('user').prefetch_related('item_view', 'orders').get(user=user)
    basket = BasketItem.objects.filter(client=client)

    # ================= ТУТ ЗНАЧЕНИЯ ИЗ МОДЕЛИ СКИДОК
    price_delivery = 500
    # ===============================================

    if basket.exists():
        for item in basket:
            order_product_copy = OrderCopyProduct.objects.create(
                product_pk=item.product.pk,
                name=item.product.name,
                description=item.product.description,
                price=item.product.price,
            )
            if item.product.product_photo.first():
                # если есть фотка, создаем новый в нужной модели через ImageFile
                order_product_copy.photo = ImageFile(item.product.product_photo.first().photo)
                order_product_copy.save()

            data = {'product': order_product_copy,
                    'count': item.qty,
                    'seller': '',
                    'price': item.price,
                    'old_price': 0,
                    }
            order_item = OrderProductBasket.objects.create(**data)
            order.order_products.add(order_item)
    if client.orders.all():
        order.number_order = len(client.orders.all())
    client.full_address = order.address
    client.city = order.city
    order.total_price = basket.total_price

    if order.delivery == 'Экспресс доставка':
        order.total_price += price_delivery
        order.delivery_price += price_delivery
    # включим флаг, что нужно поставить в очередь на оплату
    order.save()
    client.save()
    basket.delete()
    # Привяжем заказ к текущем клиенту
    client.orders.add(order)
