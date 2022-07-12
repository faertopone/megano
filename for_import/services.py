from django.http import JsonResponse, HttpResponse
from django.utils.translation import gettext as _
from products.models import Product, PropertyCategory, PropertyProduct
from shops.models import ShopProduct
import csv
from csv import reader


def list_prop_category(request):
    """Возвращает словарь со списком полей,
    необходимых для заполнения в файле свойств
    загружаемых в базу товаров"""
    new_list = PropertyCategory.objects.select_related('property').filter(category_id=int(request.GET['category']))
    text = '<ul><li><h2>Заполните в файле .cvs вот эти поля в таком же порядке:</h2></li>' \
           '<li>Наименание, Артикул, Описание, Цена, Рейтинг, Количество,</li><li>'
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
    parameter_list = ['Наименание', 'Артикул', 'Описание', 'Цена', 'Рейтинг', 'Количество']
    parameter_list += [i.property.name for i in
                       PropertyCategory.objects.select_related('property').filter(category_id=kwargs['pk'])]
    writer = csv.writer(response)
    writer.writerow(parameter_list)
    return response


def from_file_in_db(file, shop_id, category_id):
    """Считывает данные файла .csv, обрабатывает и заполняет базу данных"""
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
                product_properties_list = PropertyCategory.objects.select_related('property').filter(
                    category_id=category_id)  # это список свойств данной категории
                for i in range(len(product_properties_list)):
                    product_property_value = PropertyProduct(product=new_product,
                                                             property=product_properties_list[i].property,
                                                             value=row[6 + i])
                    product_property_value.save()

        except:
            print(f'-----------Ошибка в строке {row}')
