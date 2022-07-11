from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse
from .tasks import send_file_in_db_task
from products.models import Category
from .forms import UploadFileForm
from accounts.models import Client
from .services import from_file_in_db


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
            # Для Celery не работает???
            # send_file_in_db_task.delay(file=product_file, shop_id=shop_id, category_id=category_id)
            from_file_in_db(file=product_file, shop_id=shop_id, category_id=category_id)
            return render(request, 'for_import/upload_product.html', context=context)
