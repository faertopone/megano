from django.views import View, generic
from .models import Shops, ShopPhoto, ShopProduct


class ShopDetailVew(generic.DetailView):
	"""
	Возвращает детальную информацию о магазине
	"""
	model = Shops
	template_name = 'shops/shop.html'
	context_object_name = 'shop'

	def get(self, *args, **kwargs):
		self.extra_context = dict()

		try:
			self.extra_context['products'] = ShopProduct.objects.select_related(
				"shop", "product", "promotion"
			).filter(shop_id=kwargs['pk'])
			self.extra_context['photos'] = [
				i.photo.url for i in self.extra_context['products'][0].shop.shopphoto_set.all()
			]

		except:
			obj = Shops.objects.select_related(
				"promotion"
			).prefetch_related(
				"shopphoto_set", "shopproduct_set"
			).get(id=kwargs['pk'])
			self.extra_context = dict()
			self.extra_context['photos'] = [i.photo.url for i in obj.shopphoto_set.all()]
			self.extra_context['products'] = obj.shopproduct_set.all()

		return super().get(*args, **kwargs)
