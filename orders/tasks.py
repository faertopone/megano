from celery import shared_task
from orders.services import pay_order


@shared_task
def pay_order_task(id_order, visa_number):
    pay_order(id_order, visa_number)

