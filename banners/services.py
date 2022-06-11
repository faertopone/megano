from .models import Banners
from random import sample


def get_banners() -> list:
    """
    Функция возвращает список, с 3 случайными активными баннерами
    """
    # Проверка баннеров в БД
    if not Banners.objects.all().exists():
        return []
    list_banners = []
    banners = Banners.objects.filter(is_active=True)
    # Если баннеров мало, то просто выведем их
    if banners.count() >= 3:
        for item in banners:
            list_banners.append(item)
        random_banners = sample(list_banners, 3)
    else:
        random_banners = banners

    return random_banners
