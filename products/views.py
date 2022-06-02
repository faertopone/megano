from django.db import models
from django.utils.translation import gettext as _
from django.views import View, generic
from django.shortcuts import render, HttpResponse
from django_filters import ModelMultipleChoiceFilter, CharFilter, RangeFilter

from .filters import filterset_factory, CustomFilterSet
from .models import (Product, ProductPhoto, UserReviews, PropertyProduct,
                     Category)
from .widgets import CustomCheckboxSelectMultiple, CustomTextInput, CustomRangeWidget


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
    product_info_set = Product.objects.prefetch_related(
        "productphoto_set", "userreviews_set",
    ).get(id=int(kwargs['pk']))
    context['product'] = product_info_set
    context['properties'] = PropertyProduct.objects.filter(product_id=int(kwargs['pk'])).select_related('product')
    context['reviews'] = [i for i in context['product'].userreviews_set.all()]
    context['photos'] = [i.photo.url for i in context['product'].productphoto_set.all()]
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


class ProductListView(generic.ListView):
    template_name = "product_list.html"
    model = Product
    context_object_name = "products"
    paginate_by = 10  # TODO: ссылки на страницы пагинации

    category: Category

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        print(request.__dict__)

        category_id = self.request.resolver_match.kwargs["pk"]
        self.__class__.category = Category.objects.get(pk=category_id)

    def get_queryset(self):
        products = Product.objects.select_related("category").filter(category=self.category.pk)

        self.sort_params = self._get_sort_params()
        if (order := self.sort_params["order_by"]) is not None:
            products = products.order_by(order)

        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        # фильтр
        category_filter = self._get_filter()

        ctx = super().get_context_data(object_list=category_filter.qs, **kwargs)
        # категория каталога товаров
        ctx["category"] = self.category
        # фильтр товаров
        ctx["filter"] = category_filter
        # параметры сортировки
        ctx["sort_params"] = self.sort_params

        return ctx

    def _get_filter_class(self):
        # выбираем все свойства, участвующие в фильтре в данной категории.
        # При этом значения свойств должны быть не пустыми
        cond = models.Q(category_property__filtered=True) & \
               models.Q(product_property__product__category=self.category.pk) & \
               ~models.Q(product_property__value__isnull=True) & \
               ~models.Q(product_property__value="")
        filtered_props = self.category.properties.filter(cond)\
                             .order_by("category_property__filter_position", "name")\
                             .distinct()

        # формируем поля для filterset
        filterset_fields = {
            # Фильтр по имени товара
            "product_name": CharFilter(label=_("Название товара"), field_name="name",
                                       lookup_expr="icontains",
                                       widget=CustomTextInput(attrs={
                                          "class": "form-input form-input_full",
                                          "placeholder": _("Название товара"),
                                       }),),
            "product_price": RangeFilter(label=_("Цена"), field_name="price",
                                         widget=CustomRangeWidget(attrs={
                                            "class": "range-widget__input"
                                         }),),
        }
        for prop in filtered_props:
            # Подзапросом выбираем все уникальные значения для одного свойства товара.
            # Distinct не поможет, потому что он всегда добавляет id в select.
            subquery = PropertyProduct.objects.filter(
                product__category=self.category.pk,
                property__alias=prop.alias
            ).values("value").annotate(id=models.Min("id")).values("id")

            filterset_fields[prop.alias] = ModelMultipleChoiceFilter(
                label=prop.name,
                field_name="product_property__value",
                to_field_name="value",
                widget=CustomCheckboxSelectMultiple,
                queryset=PropertyProduct.objects.filter(id__in=subquery).only("value").order_by("value")
            )

        # возвращаем настроенный фильтр
        return filterset_factory(self.model, filterset=CustomFilterSet, model_fields=(), fields=filterset_fields)

    def _get_filter(self):
        filter_class = self._get_filter_class()
        return filter_class(self.request.GET, queryset=self.get_queryset())

    def _get_sort_params(self):
        # sorts
        price_asc = "price_asc"
        price_desc = "price_desc"
        rating_asc = "rating_asc"
        rating_desc = "rating_desc"

        # CSS classes
        sort_asc_class = "Sort-sortBy_inc"
        sort_desc_class = "Sort-sortBy_dec"

        # defaults
        sort_params = {
            "price": {
                "sort": price_asc,
                "class": None,
            },
            "rating": {
                "sort": rating_asc,
                "class": None,
            },
            "order_by": None,  # field name for model sorting
        }

        if sort_kind := self.request.GET.get("sort"):
            if sort_kind == price_asc:
                sort_params["price"].update({
                    "sort": price_desc,
                    "class": sort_desc_class,
                })
                sort_params["order_by"] = "price"
            elif sort_kind == price_desc:
                sort_params["price"].update({
                    "sort": price_asc,
                    "class": sort_asc_class,
                })
                sort_params["order_by"] = "-price"
            elif sort_kind == rating_asc:
                sort_params["rating"].update({
                    "sort": rating_desc,
                    "class": sort_desc_class,
                })
                sort_params["order_by"] = "rating"
            elif sort_kind == rating_desc:
                sort_params["rating"].update({
                    "sort": rating_asc,
                    "class": sort_asc_class,
                })
                sort_params["order_by"] = "-rating"

        return sort_params
