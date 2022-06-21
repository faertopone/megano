# TODO: Задача 20.4. Интеграция с сервисом добавления отзывов к товару.
#       Сервсис и его методы реализуются в рамках
#       "Задача 23.1. Разработка сервиса добавления отзывов"

# TODO: Задача 20.5. Интеграция с сервисом добавления товара в корзину
#       Сервис и его методы реализуются в рамках
#       "Задача 26.1. Разработка сервиса добавления товара в корзину с реальными данными"

# TODO: Задача 20.6. Интеграция с сервисом списка просмотренных товаров
#       Сервис и его методы реализуются в рамках
#       "Задача 29.1. Разработка сервиса добавления в список просмотренных товаров"

# TODO: Задача 20.7. Интеграция с сервисом скидок на товар
#       Сервис и его методы реализуются в рамках
#       "Задача 34.2. Интеграция сервиса скидок с реальными данными по скидкам"

from django.shortcuts import render, HttpResponse
import json
from django.core.cache import cache
from .models import PropertyProduct, ProductPhoto, Product
from django.http import HttpResponseRedirect, JsonResponse
from pprint import pprint


def product_detail(pk: int):
    """
    Возвращает детальную информацию о товаре с его характеристиками
    для передачи в КЭШ.
    """
    context = dict()
    context['properties'] = dict()
    info_data = PropertyProduct.objects.filter(product_id=pk)
    context['product'] = Product.objects.get(id=pk).__dict__
    context['product']['rating'] = int(context['product']['rating'])

    try:
        context['product']['photo'] = ProductPhoto.objects.filter(product_id=pk)[0].photo.url
    except:
        context['product']['photo'] = '/media/defolt.png'

    for j in info_data:
        context['properties'][j.property.name] = j.value

    return context


def count_compare_add(request):
    """
    Добавляет в КЭШ товары, выбранные пользователем к сравнению и хранит в счетчике их количество
    cache.get(str(request.session) + '_compare1') вернёт товар, добавленный сессией к сравнению
    cache.get(str(request.session) + '_compare_count') вернёт количество товаров, добавленных к сравнению
    """

    if request.GET:
        info_list = [i for i in request.GET['product_info'].split('+')]
        product_pk = int(info_list[0])
        user = info_list[1] + '_compare'
        key_count = user + '_count'
        for j in range(1, 5):
            key_product = user + str(j)

            if cache.get(key_product) is None:
                product_info = product_detail(pk=product_pk)
                cache.set(key_product, product_info, 3600)
                cache.set(key_count, j, 3600)
                break

        context = {'com_count': cache.get(key_count)}
        return JsonResponse(context)
    else:
        pass


def get_full_data_product_compare(session_key):
    """
    Формирует списки общих свойств для сравниваемых товаров:
    context['similar_properties'] общие свойства товаров со своими значениями
    context['similar_properties_unique'] общие свойства, в которых нет одинаковых значений
    """
    context = dict()
    properties_dict = dict()
    context['similar_properties'] = dict()
    context['similar_properties_unique'] = dict()
    context['similar_properties_add'] = dict()
    context['text'] = f"Сравниваем по имеющимся общим свойствам"
    context['products'] = []

    for i in range(1, 5):
        key_product = str(session_key) + '_compare' + str(i)
        obj = cache.get(key_product)
        if obj is not None:
            obj['product'].pop('_state')
            obj['cache_key'] = key_product
            context['products'].append(obj)
            for j in obj['properties']:
                if j in properties_dict:
                    properties_dict[j] += 1
                else:
                    properties_dict[j] = 1

    for property in [key for key in properties_dict if properties_dict[key] == len(context['products'])]:
        context['similar_properties'][property] = []
        for product in context['products']:
            context['similar_properties'][property].append(product['properties'][property])
    context['count'] = len(context['similar_properties'])
    if context['count'] == 0:
        context['text'] = 'У данных товаров нет общих свойств'
    else:
        for key, value in context['similar_properties'].items():
            for elem in value:
                if value.count(elem) != len(value):
                    context['similar_properties_unique'][key] = value
                else:
                    context['similar_properties_add'][key] = value
    return context


def compare_delete(request):
    """
    Удаляет товар из списка к сравнению
    """
    if request.GET:
        session_key = request.GET['cache_key'].split('_')[0]
        try:
            cache.delete(request.GET['cache_key'])
            count = cache.get(session_key + '_compare_count') - 1
            cache.set(session_key + '_compare_count', count)
            context = get_full_data_product_compare(session_key)
            context['count_compare'] = cache.get(str(session_key) + '_compare_count')
        except:
            context = dict()
        return JsonResponse(context)
