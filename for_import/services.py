from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.core.cache import cache
from django.utils.translation import gettext as _
from products.models import Product, Category, PropertyCategory
from .forms import UploadFileForm
from accounts.models import Client
from csv import reader


def list_prop_category(request):
    new_list = PropertyCategory.objects.select_related('property').filter(category_id=int(request.GET['category']))
    text = '<ul><li><h2>Заполните в файле .cvs вот эти поля в таком же порядке:</h2></li>' \
           '<li>Наименание | Артикул | Описание | Цена | Рейтинг | Наличие |</li><li>'
    index = 0
    for i in new_list:
        index += 1
        if index % 6 != 0 and index != len(new_list):
            text += str(i.property.name) + ' | '
        else:
            text += '</li><li>'
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
            # category_list = [i.category_name for i in Category.objects.all()]
            product_file = upload_file_form.cleaned_data['file'].read()
            product_str = product_file.decode("utf-8").split('\n')[1:-1]
            print('************', product_str)
            csv_reader = reader(product_str, delimiter=";", quotechar='"')
            for row_list in csv_reader:
                row = row_list[0].split(',')
                try:
                    Product.objects.filter(article=row[1]).update(
                        name=row[0], description=row[2], price=float(row[3]),
                        rating=int(row[4]))
                except:
                    new_product = Product(article=row[1], category=Category.objects.get(id=category_id),
                                          name=row[0], description=row[2],
                                          price=float(row[3]), rating=int(row[4]))
                    new_product.save()
                # if len(row) == 7:
                #     if len(Product.objects.filter(article=row[0])) != 0:
                #         Product.objects.filter(article=row[0]).update(
                #             name=row[2], description=row[3], price=float(row[4]),
                #             amount=int(row[6]))
                #     else:
                #         if not row[1] in category_list:
                #             category_list.append(row[1])
                #             new_category = Category()
                #             new_category.name = row[1]
                #             new_category.save()
                #         try:
                #             new_product = Product(article=row[0], category=Category.objects.get(name=row[1]),
                #                                   name=row[2], description=row[3],
                #                                   price=float(row[4]), photo=row[5],
                #                                   amount=int(row[6]))
                #             new_product.save()
                #         except:
                #             pass
            return render(request, 'for_import/upload_product.html', context=context)
    # else:
    #     upload_file_form = UploadFileForm()
    #     context['form'] = upload_file_form
    #     return render(request, 'for_import/upload_product.html', context=context)
