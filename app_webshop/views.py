from django.shortcuts import render
from django.views import View
from app_webshop.models import Banners
from app_webshop.services.banners import BannersServices


class Index(View):

    def get(self, request):

        # Список случайных баннеров
        banner = BannersServices()
        banners = banner.get_banners(max_banners=3)
        context = {'banners': banners}

        return render(request, 'index.html', context=context)
