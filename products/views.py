from django.shortcuts import render

from django.views import View


class GoodsView(View):
    # TODO здесь предполагаю будет реализация управления корзиной, просмотр(get)
    #  добавление(post), удаление(delete) и т.д
    pass

class PaymentView(View):
    # TODO для сервиса оплата такое предположение что вообще отдельное приложение необходимо
    pass

class DiscountView(View):
    # TODO вообще предполагаю вот скидки на товары урлы и вьюхи не нужны,
    #  так как скидка возможно будет вычисляемым полем если она есть,
    #  и автоматически применяться к товарам магазина
    pass

