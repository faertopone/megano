from celery import shared_task, app
from .services import from_file_in_db


@shared_task
def from_file_in_db_task(file, shop_id, category_id, email, file_name):
    from_file_in_db(file, shop_id, category_id, email, file_name)
