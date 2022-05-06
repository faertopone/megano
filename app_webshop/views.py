from django.shortcuts import render
from django.views import View


class Index(View):
    def get(self, request):
        context = {'text': ''}
        return render(request, 'index.html', context=context)
