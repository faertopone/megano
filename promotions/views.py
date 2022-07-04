from django.db import models
from django.views.generic import ListView, DetailView

from shops.models import ShopProduct
from utils.paginator import DisplayedPaginatedPagesMixin
from .models import Promotions
from promotions.utils.promo_filter import shop_product_filter, strategy_factory


class PromotionListView(DisplayedPaginatedPagesMixin, ListView):
    template_name = "promotion_list.html"
    model = Promotions
    context_object_name = "promotions"
    paginate_by = 30

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        # пагинатор
        ctx.update(self.get_paginated_range(ctx["page_obj"], ctx["paginator"]))

        return ctx


class PromotionDetailView(DetailView):
    template_name = "promotion_detail.html"
    model = Promotions
    context_object_name = "promotion"

    displayed_products = 8

    def get_queryset(self):
        return self.model.objects.prefetch_related("promotion_groups",)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        promo = self.get_object()
        shop_products = ShopProduct.objects.select_related(
            "shop", "product", "promotion", "product__category",
            "product__promotion_group", "product__promotion_group__promotion"
        )

        # получаем все товары со скидкой
        shop_product_filter.strategy = strategy_factory.get_promo_shop_product_filter_strategy()
        ctx["products_with_promo"] = shop_product_filter.filter(
            shop_products,
            additional_cond=models.Q(promotion=promo),
        )
        # получаем все товары, входящие в скидочную группу,
        # но у которых не назначена скидка
        shop_product_filter.strategy = strategy_factory.get_only_promo_group_shop_product_filter_strategy()
        ctx["products_in_promo_group"] = shop_product_filter.filter(
            shop_products,
            additional_cond=models.Q(product__promotion_group__promotion=promo),
        )

        # сколько товаров выводить для каждой скидки
        ctx["displayed_products"] = self.displayed_products

        return ctx
