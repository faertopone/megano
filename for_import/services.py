from django.http import JsonResponse, HttpResponse
from django.utils.translation import gettext as _
from products.models import Product, PropertyCategory, PropertyProduct, ProductPhoto
from shops.models import ShopProduct, ShopPhoto
import csv, os
from django.core.mail import send_mail
from django.conf import settings
from django.core.management import call_command
from .models import FixtureFile
from django.core.files.storage import FileSystemStorage
from .forms import FileFieldForm


def list_prop_category(request):
    """Возвращает словарь со списком полей,
    необходимых для заполнения в файле свойств
    загружаемых в базу товаров"""
    new_list = PropertyCategory.objects.select_related('property').filter(category_id=int(request.GET['category']))
    text = '<ul><li><h2>Заполните в файле .csv вот эти поля в таком же порядке:</h2></li>' \
           '<li>Наименание, Артикул, Описание, Цена, Рейтинг, Количество, Ссылка на фото,</li><li>'
    for i in new_list:
        text += str(i.property.name) + ', '
    text += '</li></ul>'
    ret_data = {'text': text, 'category_id': request.GET['category'], 'shop_id': request.GET['shop']}
    return JsonResponse(ret_data)


def export_file_csv(request, *args, **kwargs):
    """Возвращает файл .csv как шаблон
    (шапка с нужными полями)"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Dispositions'] = 'attachment; filename="users.csv"'
    parameter_list = ['Наименание', 'Артикул', 'Описание', 'Цена', 'Рейтинг', 'Количество', 'Ссылка на фото']
    parameter_list += [i.property.name for i in
                       PropertyCategory.objects.select_related('property').filter(category_id=kwargs['pk'])]
    writer = csv.writer(response)
    writer.writerow(parameter_list)
    return response


def from_file_in_db(file, shop_id, category_id, email, file_name):
    """Считывает данные файла .csv, обрабатывает и заполняет базу данных"""
    message = f'Файл обработан\n'
    for row in file:
        try:
            if len(Product.objects.filter(article=row[1])) != 0:
                new_product = Product.objects.filter(article=row[1]).update(
                    name=row[0], description=row[2], price=float(row[3]),
                    rating=int(row[4]))
                if len(ShopProduct.objects.filter(shop_id=shop_id, product=new_product)) != 0:
                    ShopProduct.objects.filter(shop_id=shop_id, product=new_product).update(
                        amount=int(row[5])
                    )

            else:
                new_product = Product(article=row[1],
                                      category_id=category_id,
                                      name=row[0], description=row[2],
                                      price=float(row[3]), rating=int(row[4]))
                new_product.save()
                new_shop_product = ShopProduct(product=new_product, shop_id=shop_id, amount=int(row[5]))
                new_shop_product.save()
                new_product_photo = ProductPhoto(product=new_product)
                new_product_photo.photo = 'products_photo/' + row[6]
                new_product_photo.save()
                product_properties_list = PropertyCategory.objects.select_related('property').filter(
                    category_id=category_id)
                for i in range(len(product_properties_list)):
                    product_property_value = PropertyProduct(product=new_product,
                                                             property=product_properties_list[i].property,
                                                             value=row[7 + i])
                    product_property_value.save()

        except Exception as err:
            message += f'Ошибка в строке {row}: {err} \n'
            print(f'-----------Ошибка в строке {row}: {err}')

    send_mail(
        subject=f'Загрузка файла {file_name}',
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )


    # call_command('loaddata', 'products/product_my_file.json', app_label='fixtures')
def load_all_fixture():
    for num in range(1, 15):
        load_data(priority=num)
    load_data()
    load_data(extension='jpg')
    load_data(extension='png')
    load_data(extension='svg')


def load_data(priority=0, extension='json'):
    img_extension_list = ['jpg', 'png', 'svg']
    fixture_file_list = FixtureFile.objects.filter(priority=priority, status='n', extension=extension)
    if len(fixture_file_list) != 0 and extension == 'json':
        for i in fixture_file_list:
            try:
                call_command('loaddata', 'media/' + str(i.file))
                i.status = 'y'
                i.save()
            except:
                print('*************Лог в файле', 'media/' + str(i.file))
                pass
    elif len(fixture_file_list) != 0 and extension in img_extension_list:

        for i in fixture_file_list:
            file_name = str(i.file).split('/')[1]
            i.delete()
            os.rename('media/admin_fixtures/' + file_name, 'media/shops_photo/' + file_name)


