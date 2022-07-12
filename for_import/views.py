from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse
from .tasks import from_file_in_db_task
from products.models import Category
from .forms import UploadFileForm
from accounts.models import Client
from csv import reader
from django.utils.translation import gettext_lazy as _


def update_product_list(request):
    """
    Выводит информацию на страницу владельца магазина,
    помогает готовить файл для импорта данных в БД
    """

    context = dict()
    context['client'] = Client.objects.select_related('user').prefetch_related('item_view').get(user=request.user)
    context['categories'] = Category.objects.all()
    context['form'] = UploadFileForm()
    if cache.get(request.user.username + '_shop'):
        context['user_shop'] = cache.get(request.user.username + '_shop')

    if not request.user.is_authenticated:
        response = HttpResponseRedirect('/accounts/login/')
        return response

    elif request.method == 'GET':
        return render(request, 'for_import/upload_product.html', context=context)

    elif request.method == 'POST':
        shop_category = request.POST['shop_category'].split('|')
        shop_id = int(shop_category[0])
        category_id = int(shop_category[1])
        upload_file_form = UploadFileForm(request.POST, request.FILES)
        if upload_file_form.is_valid():
            product_file = upload_file_form.cleaned_data['file'].read()
            product_str = product_file.decode("utf-8").split('\n')[1::]
            product_list = [i for i in reader(product_str, delimiter=",", quotechar='"')]
            from_file_in_db_task.delay(file=product_list, shop_id=shop_id, category_id=category_id)
            context['info'] = _(f"Файл {request.FILES['file']} отправлен на обработку")
            return render(request, 'for_import/upload_product.html', context=context)
