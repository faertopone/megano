from django.shortcuts import render
from django.views.generic import ListView
from banners.models import Banners
from banners.services import get_banners


class Index(ListView):
    template_name = 'index.html'
    context_object_name = 'banners'
    model = Banners

    def get_queryset(self):
        return get_banners()