from .models import Banners
from random import sample

class BannersServices:
    """
    Сервис для работы с баннерами
    """
    # Функция возвращает список случайных активных баннеров, max_banners - целое число, сколько максимально вывести баннеров
    def get_banners(self, max_banners: int):
        # Проверка баннеров в БД
        if not Banners.objects.all().exists():
            return None
        list_banners = []
        banners = Banners.objects.filter(is_active=True)
        # Если баннеров мало, то просто выведем их
        if banners.count() >= max_banners:
            for item in banners:
                list_banners.append(item)
            random_banners = sample(list_banners, max_banners)
        else:
            random_banners = banners

        return random_banners