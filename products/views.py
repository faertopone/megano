from django.views import View
from django.shortcuts import render, HttpResponse


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


class HistoryView(View):
    def get(self, request):
        context = dict()
        context['products'] = [
            {'name': 'test_name',
             'href': '#',
             'photo': {'url': 'http://127.0.0.1:8000/static/assets/img/content/home/test.jpg'},
             'new_price': '1999',
             'old_price': '5000',
             'sale': '-70%'
            }
        ]
        return render(request, 'products/historyview.html', context=context)


class ProductComment(View):
    def get(self, request, *args, **kwargs):
        context = dict()
        context['product'] = {'pk': kwargs['pk'], 'info': 'Будет база - будет инфо'}
        return render(request, 'products/product_comment.html', context=context)

    def post(self, request, *args, **kwargs):
        context = dict()
        context['users_review'] = {'name': request.POST.get('name'),
                                   'review': request.POST.get('review'),
                                   'email': request.POST.get('email')}
        return HttpResponse(content=context.values())


class ProductComparison(View):
    def get(self, request, *args, **kwargs):
        context = dict()
        context['text'] = f"Сравниваем по ID {kwargs['pk']}"
        context['products'] = [
            {'name': 'test_name',
             'href': '#',
             'photo': {'url': 'http://127.0.0.1:8000/static/assets/img/content/home/test.jpg'},
             'new_price': '1999',
             'old_price': '5000',
             'sale': '-70%'
            },
            {'name': 'test_name_1',
             'href': '#',
             'photo': {'url': 'http://127.0.0.1:8000/static/assets/img/content/home/card.jpg'},
             'new_price': '2999',
             'old_price': '3000',
             'sale': '-1%'
             }
        ]
        return render(request, 'products/historyview.html', context=context)
