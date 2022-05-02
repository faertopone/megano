from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView


class Index(View):

    def get(self, request):
        context = {'text': 'Hello world'}
        return render(request, 'index.html', context=context)
