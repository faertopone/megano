from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView
from rest_framework.request import Request

from .models import Product, Tag
from products.forms import ReviewForm


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


class ProductDetailView(DetailView):
    """ Представление для отображения детальной страницы товара """
    model = Product
    form_class = ReviewForm
    template_name = "products/product_detail.html"


    def get_context_data(self, **kwargs):
        """ Отдаёт содержание страницы при get запросе """
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.reviews.all()
        context['review_form'] = ReviewForm()
        context['shops'] = self.object.shops.all()
        context['tags'] = self.object.tags.all()
        return context

    def post(self, request: Request, pk: int):
        """ Добавление комментария к товару """
        product = self.get_object()
        review_form = ReviewForm(request.POST)

        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            if request.user.is_authenticated:
                review.username = request.user.username
                review.email = request.user.email
            review.save()
        return HttpResponseRedirect(reverse('review-detail', args=[pk]))


class ProductTagListView(ListView):
    model = Tag
    template_name = 'products/products_list.html'

    def get_context_data(self, **kwargs):
        """ Показывает список товаров по get запросу """
        context = super().get_context_data(**kwargs)
        context['products'] = Tag.objects.get(id=self.kwargs['pk']).products.all()
        return context


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
