from django.views import View, generic
from .models import Shops, ShopPhoto
from django.shortcuts import render, HttpResponse


def shop_info(request, *args, **kwargs):
	"""
	Выводит детальную информацию о магазине (о продавце)
	с товарами данного магазина, отфильтрованными по рейтингу
	"""
	context = dict()
	shop_photo_list = ShopPhoto.objects.select_related('shop').filter(shop=kwargs['pk'])
	context['photos'] = [i.photo.url for i in shop_photo_list]
	context['shop'] = shop_photo_list[1].shop
	context['products'] = [{
		'name': 'test_name',
		'href': '#',
		'photo': {'url': 'http://127.0.0.1:8000/static/assets/img/content/home/test.jpg'},
		'new_price': '1999',
		'old_price': '5000',
		'sale': '-70%'
	}, {
		'name': 'test_name_1',
		'href': '#',
		'photo': {'url': 'http://127.0.0.1:8000/static/assets/img/content/home/card.jpg'},
		'new_price': '2999',
		'old_price': '3000',
		'sale': '-1%'
	}]
	return render(request, 'shops/shop.html', context=context)
