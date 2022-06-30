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

from django.core.cache import cache
from .models import PropertyProduct, ProductPhoto, Product
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.translation import gettext as _


def product_detail(pk: int):
    """
    Возвращает детальную информацию о товаре с его характеристиками
    для передачи в КЭШ.
    """
    product = Product.objects.get(id=pk)
    context = {
        'product': {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'rating': int(product.rating),
        },
        'properties': {}
    }

    try:
        context['product']['photo'] = ProductPhoto.objects.filter(product_id=pk)[0].photo.url
    except:
        context['product']['photo'] = '/media/defolt.png'

    for j in PropertyProduct.objects.filter(product_id=pk):
        context['properties'][j.property.name] = j.value

    return context


def count_compare_add(request):
    """
    Добавляет в КЭШ товары, выбранные пользователем к сравнению и хранит в счетчике их количество
    cache.get(str(request.session) + '_compare') вернёт список товаров, добавленных сессией к сравнению
    cache.get(str(request.session) + '_compare_count') вернёт количество товаров, добавленных к сравнению
    """

    if request.GET:
        info_list = [i for i in request.GET['product_info'].split('+')]
        product_pk = int(info_list[0])
        product_info_list = []
        product_info = product_detail(pk=product_pk)
        user = info_list[1] + '_compare'
        key_count = user + '_count'

        if cache.get(user) is None:
            product_info_list.append(product_info)
        else:
            product_info_list = cache.get(user)
            product_id_list = [i['product']['id'] for i in product_info_list]
            if not product_info['product']['id'] in product_id_list:
                product_info_list.append(product_info)
        cache.set(user, product_info_list, 3600)
        cache.set(key_count, len(product_info_list), 3600)
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
    context['text'] = _("Сравниваем по имеющимся общим свойствам")
    context['products'] = []

    key_product = str(session_key) + '_compare'
    product_info_list = cache.get(key_product)
    for obj in product_info_list:
        obj['cache_key'] = key_product
        context['products'].append(obj)
        for j in obj['properties']:
            if j in properties_dict:
                properties_dict[j] += 1
            else:
                properties_dict[j] = 1

    for properties in [key for key in properties_dict if properties_dict[key] == len(context['products'])]:
        context['similar_properties'][properties] = []
        for product in context['products']:
            context['similar_properties'][properties].append(product['properties'][properties])
    context['count'] = len(context['similar_properties'])
    if context['count'] == 0:
        context['text'] = _('У данных товаров нет общих свойств')
    else:
        for key, value in context['similar_properties'].items():
            for elem in value:
                if value.count(elem) != len(value):
                    context['similar_properties_unique'][key] = value
                else:
                    context['similar_properties_add'][key] = value
    return context
