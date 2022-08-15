from datetime import datetime

from django.core.cache import cache
from django.db import models
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import DetailView, ListView
from django_filters import ModelMultipleChoiceFilter, CharFilter, RangeFilter

from accounts.services import add_product_in_history, add_product_in_history_session
from promotions.models import Promotions, PromotionGroup
from promotions.utils.promo_filter import shop_product_filter, strategy_factory
from shops.models import ShopProduct
from utils.paginator import DisplayedPaginatedPagesMixin
from .filters import filterset_factory, CustomFilterSet, SearchProductFilter
from .models import (Product, PropertyProduct, Category, Tag, UserReviews)
from .services import get_full_data_product_compare, get_user_reviews, get_lazy_load_reviews, get_count_reviews
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


class ProductDetailView(DetailView):
    """ Представление для отображения детальной страницы товара """
    model = Product
    template_name = "products/product_detail.html"

    def get_context_data(self, **kwargs):
        """ Отдаёт содержание страницы при get запросе """
        context = super().get_context_data(**kwargs)
        context['reviews'] = get_user_reviews(
            product=self.object,
            skip=int(self.request.GET.get("skip", 0)),
        )
        context["count_reviews"] = get_count_reviews(product=self.object)
        context["properties"] = {j.property.name: j.value for j in self.object.product_properties.all()}

        qs = ShopProduct.objects.filter(product=self.object)
        context["product_with_min_price"] = qs.filter(
            price_in_shop=qs.aggregate(min_price=models.Min("price_in_shop"))["min_price"]
        ).first()

        if self.request.user.is_authenticated:
            add_product_in_history(user=self.request.user, product_pk=context.get('product').pk)
        else:
            add_product_in_history_session(request=self.request, product_pk=context.get('product').pk)
        return context

    def post(self, request: HttpRequest, pk: int) -> JsonResponse:
        """ Добавление комментария к товару """
        product = self.get_object()
        obj = UserReviews.objects.create(
            user=request.user,
            product=product,
            reviews=request.POST["review"],
        )
        comment_info = {
            "user": request.user.username,
            "review": request.POST["review"],
            "created_at": datetime.strftime(obj.created_date, '%B / %d / %Y / %H:%M'),
            "client_photo": request.user.client.photo.url,
            "photo_name": request.user.client.photo.name,
            "reviews_count": UserReviews.objects.filter(product=product).count()
        }
        return JsonResponse(
            {"review": comment_info},
            status=201,
            content_type="application/json",
            safe=False
        )


class ProductTagListView(ListView):
    model = Tag
    template_name = 'products/products_list.html'

    def get_context_data(self, **kwargs):
        """ Показывает список товаров по get запросу """
        context = super().get_context_data(**kwargs)
        context['products'] = Tag.objects.get(id=self.kwargs['pk']).products.all()
        return context


class ProductCompareView(View):

    def get(self, request):
        """ Показывает список товаров по get запросу """
        session_key = request.session.session_key
        context = get_full_data_product_compare(session_key)
        for i in context['products']:
            rating = i['product']['rating']
            if rating < 100:
                i['product']['rating'] = 1
            elif rating < 300:
                i['product']['rating'] = 2
            elif rating < 600:
                i['product']['rating'] = 3
            elif rating < 900:
                i['product']['rating'] = 4
            else:
                i['product']['rating'] = 5
        context['count_compare'] = cache.get(str(session_key) + '_compare_count')
        context['session_key'] = session_key

        return render(request, 'products/compare.html', context=context)

    def post(self, request, **kwargs):
        if request.POST['product_delete']:
            session_key = str(request.session.session_key) + '_compare'
            product_list = cache.get(session_key)
            for i in product_list:
                if int(i['product']['id']) == int(request.POST['product_delete']):
                    product_list.remove(i)

            cache.set(session_key, product_list, 3600)
            count = cache.get(session_key + '_count') - 1
            cache.set(session_key + '_count', count)

        return self.get(request)


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


class BaseProductListView(DisplayedPaginatedPagesMixin, ListView):
    model = ShopProduct
    context_object_name = "products"
    paginate_by = 30

    displayed_pages = 15  # Количество страниц отображаемых в пагинаторе

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.sort_params = self._get_sort_params()

    def get_queryset(self):
        products = self.model.objects.select_related(
            "shop", "product", "promotion", "product__category"
        )

        if (order := self.sort_params["order_by"]) is not None:
            products = products.order_by(order)

        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        # параметры сортировки
        ctx["sort_params"] = self.sort_params
        # пагинатор
        ctx.update(self.get_paginated_range(ctx["page_obj"], ctx["paginator"]))

        return ctx

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
                sort_params["order_by"] = "price_in_shop"
            elif sort_kind == price_desc:
                sort_params["price"].update({
                    "sort": price_asc,
                    "class": sort_asc_class,
                })
                sort_params["order_by"] = "-price_in_shop"
            elif sort_kind == rating_asc:
                sort_params["rating"].update({
                    "sort": rating_desc,
                    "class": sort_desc_class,
                })
                sort_params["order_by"] = "product__rating"
            elif sort_kind == rating_desc:
                sort_params["rating"].update({
                    "sort": rating_asc,
                    "class": sort_asc_class,
                })
                sort_params["order_by"] = "-product__rating"

        return sort_params


class CategoryProductListView(BaseProductListView):
    template_name = "product_list.html"

    category: Category

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        category_id = self.request.resolver_match.kwargs["pk"]
        self.__class__.category = Category.objects.get(pk=category_id)

    def get_queryset(self):
        products = super().get_queryset().filter(product__category=self.category.pk)

        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        # фильтр
        category_filter = self._get_filter()

        ctx = super().get_context_data(object_list=category_filter.qs, **kwargs)
        # категория каталога товаров
        ctx["category"] = self.category
        # фильтр товаров
        ctx["filter"] = category_filter

        return ctx

    def _get_filter_class(self):
        # выбираем все свойства, участвующие в фильтре в данной категории.
        # При этом значения свойств должны быть не пустыми
        cond = models.Q(category_property__filtered=True) & \
               models.Q(product_property__product__category=self.category.pk) & \
               ~models.Q(product_property__value__isnull=True) & \
               ~models.Q(product_property__value="")
        filtered_props = self.category.properties.filter(cond) \
            .order_by("category_property__filter_position", "name") \
            .distinct()

        # формируем поля для filterset
        filterset_fields = {
            # Фильтр по имени товара
            "product_name": CharFilter(label=_("Название товара"), field_name="product__name",
                                       lookup_expr="icontains",
                                       widget=CustomTextInput(attrs={
                                           "class": "form-input form-input_full",
                                           "placeholder": _("Название товара"),
                                       }), ),
            # Фильтр по цене
            "product_price": RangeFilter(label=_("Цена"), field_name="price_in_shop",
                                         widget=CustomRangeWidget(attrs={
                                             "class": "range-widget__input"
                                         }), ),
        }
        for prop in filtered_props:
            # Подзапросом выбираем все уникальные значения для одного свойства товара.
            # Distinct не поможет, потому что он всегда добавляет id в select.
            subquery = models.Subquery(PropertyProduct.objects.filter(
                product__category=self.category.pk,
                property__alias=prop.alias
            ).values("value").annotate(id=models.Min("id")).values("id"))

            # Добавляем фильтр для свойства товара
            filterset_fields[prop.alias] = ModelMultipleChoiceFilter(
                label=prop.name,
                field_name="product__product_property__value",
                to_field_name="value",
                widget=CustomCheckboxSelectMultiple,
                queryset=PropertyProduct.objects.filter(id__in=subquery).only("value").order_by("value")
            )

        # возвращаем настроенный фильтр
        return filterset_factory(self.model, filterset=CustomFilterSet, model_fields=(), fields=filterset_fields)

    def _get_filter(self):
        filter_class = self._get_filter_class()
        return filter_class(self.request.GET, queryset=self.get_queryset())


class PromotionProductListView(BaseProductListView):
    template_name = "promotion_product_list.html"

    promotion: Promotions

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        promotion_id = self.request.resolver_match.kwargs["pk"]
        self.__class__.promotion = Promotions.objects.get(pk=promotion_id)

    def get_queryset(self):
        shop_product_filter.strategy = strategy_factory.get_promo_shop_product_filter_strategy()

        products = shop_product_filter.filter(
            super().get_queryset(),
            additional_cond=models.Q(promotion=self.promotion)
        )

        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)

        # скидка
        ctx["promotion"] = self.promotion

        return ctx


class PromotionGroupProductListView(BaseProductListView):
    template_name = "promotion_product_list.html"

    promotion_group: PromotionGroup

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        promotion_group_id = self.request.resolver_match.kwargs["pk"]
        self.__class__.promotion_group = PromotionGroup.objects.select_related(
            "promotion",
        ).get(pk=promotion_group_id)

    def get_queryset(self):
        shop_product_filter.strategy = strategy_factory.get_only_promo_group_shop_product_filter_strategy()

        products = shop_product_filter.filter(
            super().get_queryset(),
            additional_cond=models.Q(product__promotion_group=self.promotion_group)
        )

        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)

        # группа скидок
        ctx["promotion_group"] = self.promotion_group
        # скидка
        ctx["promotion"] = self.promotion_group.promotion

        return ctx


class SearchedProductListView(BaseProductListView):
    template_name = "searched_product_list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        # фильтр
        search_filter = self._get_filter()

        ctx = super().get_context_data(object_list=search_filter.qs, **kwargs)

        return ctx

    def _get_filter(self):
        return SearchProductFilter(self.request.GET, queryset=self.get_queryset())


def lazy_load_reviews_views(request):
    """ Подгружает по 5 отзывов к товару при нажатии на кнопку показать ещё """
    data = get_lazy_load_reviews(
        product_id=request.GET.get("product_id"),
        skip=int(request.GET.get("skip", 0))
    )
    return JsonResponse(
        {"reviews": data},
        status=200,
        content_type="application/json",
        safe=False
    )


def empty(request):
    return render(request, 'emptys/empty.html', {})
