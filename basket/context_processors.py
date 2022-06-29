from basket.basket import Basket


def basket(request):
    """
    При помощи этого контекст процессора у нас при загрузке страницы
    инициализируется класс Basket
    """
    return {'basket':  Basket(request)}
