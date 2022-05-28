from django.views import View
from django.shortcuts import render, HttpResponse
from .models import Product, ProductPhoto, UserReviews, PropertyProduct


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
            {
                'name': 'test_name',
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


def product_detail_review(request, *args, **kwargs):
    """
    Выводит детальную информацию о товаре с возможностью добавить отзыв к нему.
    Отзыв могут оставлять только зарегистрированные пользователи.
    """
    context = dict()
    context['properties'] = PropertyProduct.objects.filter(product_id=int(kwargs['pk'])).select_related('product')
    context['reviews'] = UserReviews.objects.filter(product_id=int(kwargs['pk']))
    context['product'] = context['properties'][0].product
    context['photos'] = [i.photo.url for i in ProductPhoto.objects.filter(product_id=int(kwargs['pk']))]
    context['reviews_count'] = len(context['reviews'])
    # TODO здесь надо будет дорабатывать после окончательной работы над моделями,
    #  надо ещё добавить модель ProductShop
    context['shops'] = [
        {'name': 'testshop1', 'price': 22000},
        {'name': 'testshop2', 'price': 21700},
        {'name': 'testshop3', 'price': 20100},
        {'name': 'testshop4', 'price': 19999},
    ]

    if request.method == "GET":
        return render(request, 'products/product_detail.html', context=context)

    if request.method == "POST":
        try:
            UserReviews.objects.create(
                user=request.user,
                reviews=request.POST.get('review'),
                product=context['product'])
            return render(request, 'products/product_detail.html', context=context)
        except:
            context['users_review'] = '<h1>Вы не авторизированы.</h1>'
            return HttpResponse(content=context['users_review'])


class ProductComparison(View):
    def get(self, request, *args, **kwargs):
        context = dict()
        context['text'] = f"Сравниваем по ID {kwargs['pk']}"
        context['products'] = [
            {
                'name': 'test_name',
                'href': '#',
                'photo': {'url': 'http://127.0.0.1:8000/static/assets/img/content/home/test.jpg'},
                'new_price': '1999',
                'old_price': '5000',
                'sale': '-70%'
            },
            {
                'name': 'test_name_1',
                'href': '#',
                'photo': {'url': 'http://127.0.0.1:8000/static/assets/img/content/home/card.jpg'},
                'new_price': '2999',
                'old_price': '3000',
                'sale': '-1%'
             }
        ]
        return render(request, 'products/historyview.html', context=context)
