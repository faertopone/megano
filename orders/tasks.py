from celery import shared_task
from orders.services import pay_order_


@shared_task
def pay_order_task(id_order, visa_number):
    pay_order_(id_order, visa_number)
