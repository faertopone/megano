import csv
import os
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.conf import settings

from products.models import Product, PropertyCategory, PropertyProduct, ProductPhoto, Category
from shops.models import ShopProduct, ShopPhoto
from accounts.models import Client

from for_import.models import FixtureFile
from for_import.load_fixtur_logic import my_load_data

img_extension_list = ['jpeg', 'jpg', 'png', 'svg', 'webp', 'bmp']


def list_prop_category(request):
    """Возвращает словарь со списком полей,
    необходимых для заполнения в файле свойств
    загружаемых в базу товаров"""
    new_list = PropertyCategory.objects.select_related('property').filter(category_id=int(request.GET['category']))
    text = '<ul><li><h2>Заполните в файле .csv вот эти поля в таком же порядке:</h2></li>' \
           '<li>Наименание, Артикул, Описание, Цена, Рейтинг, Количество, Ссылка на фото, Цена магазина</li><li>'
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
    parameter_list = ['Наименание', 'Артикул', 'Описание', 'Цена', 'Рейтинг',
                      'Количество', 'Ссылка на фото', 'Цена магазина']
    parameter_list += [i.property.name for i in
                       PropertyCategory.objects.select_related('property').filter(category_id=kwargs['pk'])]
    writer = csv.writer(response)
    writer.writerow(parameter_list)
    return response


def from_file_in_db(file, shop_id, category_id, email, file_name):
    """Считывает данные файла .csv, обрабатывает и заполняет базу данных"""
    message = 'Файл обработан\n'
    for row in file:
        try:
            new_product = Product()
            new_shop_product = ShopProduct()
            if len(Product.objects.filter(article=row[1])) != 0:
                new_product = Product.objects.get(article=row[1])
                if len(ShopProduct.objects.filter(shop_id=shop_id, product=new_product)) != 0:
                    new_shop_product = ShopProduct.objects.get(shop_id=shop_id, product=new_product)

            new_product.name = row[0]
            new_product.article = row[1]
            new_product.description = row[2]
            new_product.price = float(row[3])
            new_product.rating = int(row[4])
            new_product.category_id = category_id
            new_product.save()

            new_shop_product.product = new_product
            new_shop_product.shop_id = shop_id
            new_shop_product.amount = int(row[5])
            new_shop_product.price_in_shop = float(row[7])
            new_shop_product.save()

            if len(ProductPhoto.objects.filter(product=new_product, photo='products_photo/' + row[6])) == 0:
                new_product_photo = ProductPhoto(product=new_product)
                new_product_photo.photo = 'products_photo/' + row[6]
                new_product_photo.save()

            product_properties_list = PropertyCategory.objects.select_related('property').filter(
                category_id=category_id)
            for i in range(len(product_properties_list)):
                if len(PropertyProduct.objects.filter(product=new_product,
                                                      property=product_properties_list[i].property)) == 0:
                    product_property_value = PropertyProduct(product=new_product,
                                                             property=product_properties_list[i].property,
                                                             value=row[8 + i])
                else:
                    product_property_value = PropertyProduct.objects.get(product=new_product,
                                                                         property=product_properties_list[i].property)
                    product_property_value.value = row[8 + i]

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


def load_all_fixture():
    """Обрабатывает загруженные файлы фикстур в порядке очерёдности"""
    for num in range(1, 15):
        load_data(priority=num)
    load_data()
    for extension in img_extension_list:
        load_data(extension=extension)


def load_data(priority=0, extension='json'):
    """Анализирует загруженный файл фикстуры и обновляет базу данных по его данным"""
    # img_extension_list = ['jpeg', 'jpg', 'png', 'svg', 'WebP']
    fixture_file_list = FixtureFile.objects.filter(priority=priority, status='n', extension=extension)
    if len(fixture_file_list) != 0 and extension == 'json':
        for i in fixture_file_list:
            my_load_data(str(i.file))
            i.status = 'y'
            i.save()
    elif len(fixture_file_list) != 0 and extension in img_extension_list:
        product_photo_list = [str(i.photo.url).split('/')[-1] for i in ProductPhoto.objects.all() if i.photo]
        shop_photo_list = [str(i.photo.url).split('/')[-1] for i in ShopPhoto.objects.all() if i.photo]
        client_photo_list = [str(i.photo.url).split('/')[-1] for i in Client.objects.all() if i.photo]
        categories_photo_list = [str(i.icon_photo.url).split('/')[-1] for i in Category.objects.all() if i.icon_photo]
        for i in fixture_file_list:
            moving_a_file(i, product_photo_list, 'media/products_photo/')
            moving_a_file(i, shop_photo_list, 'media/shops_photo/')
            moving_a_file(i, client_photo_list, 'media/accounts/')
            moving_a_file(i, categories_photo_list, 'media/categories/')


def moving_a_file(file, photo_list, new_directory):
    """Распределяет файлы загруженных изображений по необходимым директориям"""
    file_name = str(file.file).split('/')[1]
    if file_name in photo_list:
        file.delete()
        try:
            os.remove(new_directory + file_name)
        except FileNotFoundError:
            pass
        os.rename('media/admin_fixtures/' + file_name, new_directory + file_name)
