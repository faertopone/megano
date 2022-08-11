import datetime
from django.db import models
from django.views.generic import ListView
from banners.models import Banners
from banners.services import get_banners
from products.models import Product
from promotions.models import PromotionsShowProduct
from shops.models import ShopProduct


class Index(ListView):
    template_name = 'index.html'
    context_object_name = 'banners'
    model = Banners

    def get_queryset(self):
        return get_banners()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # товар дня
        promo = PromotionsShowProduct.objects.first()
        context['promotion'] = promo
        context['data'] = datetime.datetime.now() + datetime.timedelta(days=promo.limit_day_show_product)
        return context

    def get(self, *args, **kwargs):
        self.extra_context = dict()
        shop_products = ShopProduct.objects.select_related("shop", "product", "promotion")
        # популярные товары
        self.extra_context['products'] = shop_products.filter(product__rating__gte=100).all()
        # товары со скидкой
        self.extra_context["discounts"] = shop_products.filter(~models.Q(promotion__isnull=True))[:4]

        return super().get(*args, **kwargs)
