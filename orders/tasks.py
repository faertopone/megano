from celery import shared_task
from orders.models import Order
from orders.services import pay_order
from django.utils.translation import gettext_lazy as _


@shared_task(name="Оплата заказов")
def pay_order_task(id_order, visa_number):
    pay_order(id_order, visa_number)


@shared_task(name=_('Автономная оплата заказов'))
def pay_order_automatic():
    """
    Функция ищет не оплаченные заказы и оплачиваем с вероятностью 50%
    """

    orders = Order.objects.filter(need_pay=True)
    for order in orders:
        if order.number_visa % 2 == 0:
            # Имитация оплаты заказа
            order.status_pay = True
            order.transaction = f'{(order.number_visa // 6) * 3}'
            order.error_pay = None
        else:
            order.status_pay = False
            order.error_pay = f'Карта с №{str(order.number_visa)} - не действительна!'

        order.need_pay = False
        order.save()
