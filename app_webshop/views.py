from django.views.generic import ListView
from banners.models import Banners
from banners.services import get_banners
from shops.models import ShopProduct


class Index(ListView):
    template_name = 'index.html'
    context_object_name = 'banners'
    model = Banners

    def get_queryset(self):
        return get_banners()

    def get(self, *args, **kwargs):
        self.extra_context = dict()
        self.extra_context['products'] = ShopProduct.objects.select_related(
            "shop", "product", "promotion"
        ).all()

        return super().get(*args, **kwargs)
