from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse
from .tasks import from_file_in_db_task
from products.models import Category
from .forms import UploadFileForm, FileFieldForm
from .models import FixtureFile
from accounts.models import Client
from csv import reader
from django.utils.translation import gettext as _
from django.views.generic.edit import View
from django.core.management import call_command
from django.conf import settings


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
            from_file_in_db_task.delay(file=product_list, shop_id=shop_id,
                                       category_id=category_id, email=str(request.user.email),
                                       file_name=str(request.FILES['file']))
            text_1 = _("Файл ")
            text_2 = _(" отправлен на обработку. Отчет отправлен на ")
            context['info'] = text_1 + str(request.FILES['file']) + text_2 + str(request.user.email)
            return render(request, 'for_import/upload_product.html', context=context)


class FileFieldView(View):
    # данная функция в разработке
    context = dict()

    def get(self, request):
        self.context['form'] = FileFieldForm()
        self.context['client'] = Client.objects.select_related('user').prefetch_related('item_view').get(
            user=request.user)
        return render(request, 'for_import/update_fixture.html', context=self.context)

    def post(self, request):
        upload_file_form = FileFieldForm(request.POST, request.FILES)
        if upload_file_form.is_valid():
            files = request.FILES.getlist('file_field')
            for f in files:
                fixture_file = FixtureFile(file=f)
                fixture_file.save()
                # call_command('loaddata', fixture_file.file, app_label='media')

        else:
            return self.form_invalid(upload_file_form)
        return HttpResponse('<h1>Файлы добавлены в базу и отправлены в обработку</h1> '
                            '<h1>Отчет будет отправлен Вам на почту</h1>'
                            '<p> <a href="/admin">Вернуться в административный рдел</a></p>'
                            '<p> <a href="/">Вернуться на гланую страницу сайта</a></p>')
