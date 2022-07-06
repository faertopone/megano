from django.views import generic
from .models import Shops, ShopProduct


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
