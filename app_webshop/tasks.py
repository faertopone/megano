from celery import shared_task
from django.utils.translation import gettext_lazy as _


@shared_task(name=_('Товар дня, время обновления'))
def show_product_promotion_task(limit_day):
    pass
