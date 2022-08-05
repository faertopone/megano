from celery import shared_task

from for_import.services import from_file_in_db, load_all_fixture


@shared_task
def from_file_in_db_task(file, shop_id, category_id, email, file_name):
    from_file_in_db(file, shop_id, category_id, email, file_name)


@shared_task
def load_all_fixture_task():
    load_all_fixture()
