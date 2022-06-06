from django.shortcuts import render
from django.views import View
from .services import BannersServices


class Index(View):

    def get(self, request):
        # Список случайных баннеров
        banner = BannersServices()
        banners = banner.get_banners()
        context = {'banners': banners}

        return render(request, 'index.html', context=context)
