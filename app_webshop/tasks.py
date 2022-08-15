from random import sample
from celery import shared_task
from products.models import Product
from promotions.models import PromotionsShowProduct


@shared_task(name='Автономно смена товара')
def show_promo_product():
    """
    Выбирает 1 рандомный товар из всего списка
    """
    promo = PromotionsShowProduct.objects.first()
    products = Product.objects.all()
    list_products = []
    for i in products:
        list_products.append(i)
    product_day_show = sample(list_products, 1)
    promo.product_show = product_day_show[0]
    promo.save()
