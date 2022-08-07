from django.core.cache import cache
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic.edit import View

from csv import reader
from products.models import Category
from accounts.models import Client
from shops.models import Shops

from for_import.tasks import from_file_in_db_task, load_all_fixture_task
from for_import.forms import UploadFileForm, FileFieldForm
from for_import.models import FixtureFile


def update_product_list(request):
    """
    Выводит информацию на страницу владельца магазина,
    помогает готовить файл для импорта данных в БД
    """
    if (not request.user.is_authenticated
            or (not cache.get(request.user.username + '_shop')
                and not request.user.is_superuser)):
            # or len(ShopUser.objects.filter(user=request.user)) == 0
            # or not request.user.is_superuser):
        return redirect(reverse('login'))
    else:

        context = dict()
        context['client'] = Client.objects.select_related('user').prefetch_related('item_view').get(user=request.user)
        context['categories'] = Category.objects.all()
        context['form'] = UploadFileForm()
        # if cache.get(request.user.username + '_shop'):
        context['user_shop'] = cache.get(request.user.username + '_shop')

        if request.method == 'GET':
            if not context['user_shop']:
                context['user_shop'] = [i for i in Shops.objects.all()]
            # if (len(ShopUser.objects.filter(user=request.user)) == 0
            #         and not request.user.is_superuser):
            #     return redirect(reverse('login'))
            return render(request, 'for_import/upload_product.html', context=context)

        elif request.method == 'POST':
            # if (len(ShopUser.objects.filter(user=request.user)) == 0
            #         and not request.user.is_superuser):
            #     return redirect(reverse('login'))
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
    """
    Выводит информацию на страницу для загрузки фикстур.
    Доступна только администратору
    """
    context = dict()

    def get(self, request):
        if request.user.is_superuser:
            self.context['form'] = FileFieldForm()
            self.context['client'] = Client.objects.select_related('user').prefetch_related('item_view').get(
                user=request.user)
            return render(request, 'for_import/update_fixture.html', context=self.context)
        else:
            return redirect(reverse('login'))

    def post(self, request):
        if request.user.is_superuser:
            upload_file_form = FileFieldForm(request.POST, request.FILES)
            if upload_file_form.is_valid():
                files = request.FILES.getlist('file_field')
                for f in files:
                    fixture_file = FixtureFile(file=f)
                    fixture_file.save()
                load_all_fixture_task.delay()
                self.context['form'] = FileFieldForm()
                self.context['client'] = Client.objects.select_related('user').prefetch_related('item_view').get(
                    user=request.user)
                self.context['info'] = [_('Файлы добавлены в базу и отправлены на '
                                        'обработку.'),  _('Посмотреть файл ошибок'),
                                        '/media/admin_fixtures/errors_file.txt']
                return render(request, 'for_import/update_fixture.html', context=self.context)

            else:
                return self.form_invalid(upload_file_form)

        else:
            return redirect(reverse('login'))
