from datetime import datetime, timedelta
from random import sample
from celery import shared_task
from celery.schedules import crontab
from config.celery import app
from products.models import Product
from promotions.models import PromotionsShowProduct
from django_celery_beat.models import CrontabSchedule, PeriodicTask


@shared_task(name='Автономно смена товара')
def show_promo_product():
    """
    Выбирает 1 рандомный товар из всего списка
    """
    if Product.objects.all().exists():
        promo = PromotionsShowProduct.objects.first()
        products = Product.objects.all()
        list_products = []
        for i in products:
            list_products.append(i)
        product_day_show = sample(list_products, 1)
        promo.product_show = product_day_show[0]
        promo.save()


def setting_product_show():
    """
    Функция настройки переодичности обновления товара дня
    """

    if not PromotionsShowProduct.objects.all().exists():
        promo = PromotionsShowProduct.objects.create(product_show=Product.objects.first())
    else:
        promo = PromotionsShowProduct.objects.first()
    dt_now = datetime.now()
    last_day = dt_now + timedelta(days=promo.limit_day_show_product)
    app.conf.beat_schedule = {
        'Товар дня - настройка периодичности отображения': {
            # Если в @shared_task(name='Автономно смена товара') - есть имя, то 'task' имя пишем, иначе путь полный
            # 'app_webshop.tasks.show_promo_product'
            'task': 'Автономно смена товара',
            'schedule': crontab(hour=0, minute=0, day_of_week=f'{dt_now.day}-{last_day.day}'),
            # 'schedule': crontab(minute=f'*/{promo.limit_day_show_product}'),
        },
    }


setting_product_show()






