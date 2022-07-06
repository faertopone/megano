from celery import shared_task

from basket.services import delete_old_baskets


@shared_task
def delete_old_baskets_task(minutes=1440):
    delete_old_baskets(minutes)