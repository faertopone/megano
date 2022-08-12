from django.views import generic
from .models import Shops, ShopProduct
from products.views import BaseProductListView


class ShopDetailVew(generic.DetailView):
    """
    Возвращает детальную информацию о магазине
    """
    model = Shops
    template_name = 'shops/shop.html'
    context_object_name = 'shop'

    def get(self, *args, **kwargs):
        self.extra_context = dict()
        self.extra_context['products'] = ShopProduct.objects.select_related(
            "shop", "product", "promotion"
        ).filter(shop_id=kwargs['pk'])

        try:
            self.extra_context['photos'] = [
                i.photo.url for i in self.extra_context['products'][0].shop.shop_photos.all()
            ]
        except IndexError:
            obj = Shops.objects.select_related(
                "promotion"
            ).prefetch_related(
                "shop_photos", "shop_product"
            ).get(id=kwargs['pk'])

            self.extra_context['photos'] = [i.photo.url for i in obj.shop_photos.all()]
            self.extra_context['products'] = obj.shop_product.all()

        return super().get(*args, **kwargs)


class ShopListView(generic.ListView):
    model = Shops
    template_name = 'shops/shops_list.html'
    context_object_name = 'shops'
    queryset = Shops.objects.prefetch_related("shop_photos").all()


class ShopProductListView(BaseProductListView):
    template_name = "shop_product_list.html"
    shop_id: int

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.shop_id = self.request.resolver_match.kwargs["pk"]

    def get_queryset(self, **kwargs):
        products = super().get_queryset().filter(shop=self.shop_id)
        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(object_list=object_list, **kwargs)
        ctx["shop"] = Shops.objects.get(id=self.shop_id)
        ctx['photos'] = [i.photo.url for i in ctx['shop'].shop_photos.all()]

        return ctx
