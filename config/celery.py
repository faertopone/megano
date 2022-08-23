import os
from celery.schedules import crontab
from django.conf import settings
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# По умолчание создадим период 1 день
app.conf.beat_schedule = {
    'Товар дня - настройка периодичности отображения': {
        # Если в @shared_task(name='Автономно смена товара') - есть имя, то 'task' имя пишем, иначе путь полный
        # 'app_webshop.tasks.show_promo_product'
        'task': 'Автономно смена товара',
        'schedule': crontab(hour=0, minute=0, day_of_month='*'),
    },
}
