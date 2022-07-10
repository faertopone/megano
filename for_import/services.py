from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.core.cache import cache
from django.utils.translation import gettext as _
from products.models import Product, Category, PropertyCategory, ProductPhoto, PropertyProduct, Property
from shops.models import ShopProduct
from .forms import UploadFileForm
from accounts.models import Client
import csv
from csv import reader


def list_prop_category(request):
    new_list = PropertyCategory.objects.select_related('property').filter(category_id=int(request.GET['category']))
    text = '<ul><li><h2>Заполните в файле .cvs вот эти поля в таком же порядке:</h2></li>' \
           '<li>Наименание, Артикул, Описание, Цена, Рейтинг, Количество,</li><li>'
    for i in new_list:
        text += str(i.property.name) + ', '
    text += '</li></ul>'
    ret_data = {'text': text, 'category_id': request.GET['category'], 'shop_id': request.GET['shop']}
    return JsonResponse(ret_data)


def update_product_list(request):
    """
    Loading data into the model 'ProductProfile' from a file
    :param request:
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
            csv_reader = reader(product_str, delimiter=";", quotechar='"')
            for row_list in csv_reader:
                try:
                    row = row_list[0].split(',')
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
                    print(f'++++++++++++++++++++++++++++++Ошибка в строке {row_list}', Exception.__dict__)
            return render(request, 'for_import/upload_product.html', context=context)
        # else:
        #     upload_file_form = UploadFileForm()
        #     context['form'] = upload_file_form
        #     return render(request, 'for_import/upload_product.html', context=context)


def export_file_csv(request, *args, **kwargs):
    response = HttpResponse(content_type='text/csv')
    response['Content-Dispositions'] = 'attachment; filename="users.csv"'
    parameter_list = ['Наименание', 'Артикул', 'Описание', 'Цена', 'Рейтинг', 'Количество']
    parameter_list += [i.property.name for i in
                       PropertyCategory.objects.select_related('property').filter(category_id=kwargs['pk'])]
    writer = csv.writer(response)
    writer.writerow(parameter_list)
    return response
