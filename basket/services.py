from basket.models import BasketItem
from datetime import datetime, timedelta


def delete_old_baskets(minites):
    """Удаляем корзинки на сессиях, которые не обновлялись minutes минут"""
    now = datetime.now()
    check_date = now - timedelta(minutes=minites)
    baskets = BasketItem.objects.filter(updated__gte=check_date, client__isnull=True)
    baskets.delete()
