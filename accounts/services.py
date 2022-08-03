from django.contrib.auth.models import User
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings

from products.models import Product
from .models import Client


def send_client_email(user_id, domain, subject, template):
    """Отправка письма """
    user = User.objects.get(id=user_id)
    message = render_to_string(
        'accounts/{}_email.html'.format(template), {
            'user': user,
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )


def initial_form_profile_new(request: HttpRequest) -> dict:
    """
    Функция инициализирует начальные значения Профиля
    """
    client = Client.objects.select_related('user').prefetch_related('item_view').get(user=request.user)
    initial_client = {
        'phone': client.phone,
        'patronymic': client.patronymic,
        'id_user': client.user.id,
        'first_name': client.user.first_name,
        'last_name': client.user.last_name,
        'email': client.user.email,
        'limit_items_views': client.limit_items_views,
        'item_in_page_views': client.item_in_page_views
    }
    return initial_client


def save_dop_parametrs(request: HttpRequest, form):  # noqa: C901
    """
    Функция сохраняет данные, которые были изменены на странице редактирования профиля
    """
    client = Client.objects.select_related('user').prefetch_related('item_view').get(user=request.user)
    # Если данные были изменены, то:
    if form.has_changed():
        # Список какие поля были изменены
        change_data_list = form.changed_data
        # Извлечем данные с формы
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('last_name')
        avatar = form.cleaned_data.get('photo')
        phone = form.cleaned_data.get('phone')
        email = form.cleaned_data.get('email')
        patronymic = form.cleaned_data.get('patronymic')
        password = form.cleaned_data.get('password1')
        limit_items_views = form.cleaned_data.get('limit_items_views')
        item_in_page_views = form.cleaned_data.get('item_in_page_views')

        if 'first_name' in change_data_list:
            client.user.first_name = first_name
        if 'last_name' in change_data_list:
            client.user.last_name = last_name
        if 'photo' in change_data_list:
            client.photo = avatar
        if 'phone' in change_data_list:
            client.phone = phone
        if 'email' in change_data_list:
            client.user.email = email
        if 'patronymic' in change_data_list:
            client.patronymic = patronymic
        if 'password1' in change_data_list:
            client.user.set_password(password)
        if 'limit_items_views' in change_data_list:
            client.limit_items_views = limit_items_views
        if 'item_in_page_views' in change_data_list:
            client.item_in_page_views = item_in_page_views

        client.user.save()
        client.save()


def add_product_in_history(user: object, product_pk: int):
    """
    Функция, добавляет просмотренный товар в БД
    """
    client = Client.objects.select_related('user').prefetch_related('item_view').get(user=user)
    product = Product.objects.get(pk=product_pk)
    list_viewers_products = client.item_view.all()
    # Если этого продукта нет еще в истории, то добавим его
    if not (product in list_viewers_products):
        client.item_view.add(product)


def add_product_in_history_session(request: HttpRequest, product_pk: int):
    """
    Функция, добавляет просмотренный товар в сессию пользователя
    """

    # если еще не было товаров в сессии, создадим список и добавим этот товар
    if not request.session.get('products_session'):
        product_history_list = list()
        product_history_list.append(product_pk)
        request.session['products_session'] = product_history_list
    else:
        # если там уже добавлен товар, то сначала извлекаем список товаров
        product_list = request.session.get('products_session')
        # Добавляем новый товар если такого нет в списке
        if not (product_pk in product_list):
            product_list.append(product_pk)
            # обновляем сессию с товарами
            request.session['products_session'] = product_list


def get_context_data(user) -> list:
    """
    Функция для вычисления context['list_item_views'] - Вывод товаров для просмотра и
    context['all_items_complete'] - флаг, что все допустимы товары вывели
    """

    client = Client.objects.select_related('user').prefetch_related('item_view').get(user=user)
    item_in_page_views_check = client.item_in_page_views_check()
    max_limit = client.limit_items_views
    if len(client.item_view.all()) > 0:
        list_item_views = client.item_view.all().order_by('-client_products_views__id')[:item_in_page_views_check]
        if len(client.item_view.all()[:max_limit]) <= item_in_page_views_check:
            all_items_complete = False
        else:
            all_items_complete = True
    else:
        list_item_views = []
        all_items_complete = True

    return [list_item_views, all_items_complete]


def get_context_data_ajax(user, items_in_page) -> list:
    """
    Функция возвращает товары, которые нужно добавить на страницу просмотров
    """
    client = Client.objects.select_related('user').prefetch_related('item_view').get(user=user)
    limit_items_views = client.limit_items_views
    item_in_page_views_check = client.item_in_page_views_check()
    list_item_views = client.item_view.all().order_by('-client_products_views__id')[:limit_items_views]

    # Добавим на вывод на страницу N товаров
    # Флаг, который говорит что все элементы передали и больше новых нет
    flag_items_complete = False
    end_element = items_in_page + item_in_page_views_check
    if end_element >= len(list_item_views):
        end_element = limit_items_views
        flag_items_complete = True

    list_item_views = list_item_views[items_in_page:end_element]
    list_in_page = []
    photo = '#'
    for item in list_item_views:
        for i in item.product_photo.all():
            photo = i.photo.url
        list_in_page.append({'name': item.name,
                             'price': item.price,
                             'category': item.category.category_name,
                             'item_pk': item.pk,
                             'photo': photo,
                             })
        # обнулим переменную с адресом фотки
        photo = '#'
    return [list_in_page, flag_items_complete]
