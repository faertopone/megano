from django.views import generic
from .models import Shops
from products.views import BaseProductListView


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
