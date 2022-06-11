from django.contrib.auth.models import User
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings

from products.models import Product
from .models import Client, HistoryView


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


def initial_form_profile(request: HttpRequest) -> list:
    """
    Функция инициализирует начальные значения Профиля
    """
    user = User.objects.get(pk=request.user.pk)
    client = Client.objects.select_related('user').get(user=request.user)
    initial_client = {
        'phone': client.phone,
        'patronymic': client.patronymic,
        'id_user': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email
    }
    return [initial_client, client]


def post_context(request: HttpRequest, form) -> object:
    """
     Представления Профиля при запросе POST и изменения данных, которые были изменены
     """
    messages = ''
    initial_data_all = initial_form_profile(request=request)
    client = initial_data_all[1]
    form = form
    if form.is_valid():
        # Если изменения были в форме, то выполним это
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

            client.save()
            messages = 'Данные успешно сохранены!'

    context = {'form': form,
               'client': client,
               'msg': messages}
    return context


def add_product_in_history(user: object, product_pk: int):
    """
    Функция, добавляет просмотренный товар в БД
    """
    client = Client.objects.select_related('user').get(user=user)
    client_history = HistoryView.objects.prefetch_related('item_view').get(client=client)
    product = Product.objects.get(pk=product_pk)
    list_viewers_products = client_history.item_view.all()
    # Если этого продукта нет еще в истории, то добавим его
    if not (product in list_viewers_products):
        client_history.item_view.add(product)


def add_product_in_history_session(request: HttpRequest):
    """
    Функция, добавляет просмотренный товар сессию пользователя
    """
    pass


def get_context_data(user) -> list:
    """
    Функция для вычисления context['list_item_views'] - Вывод товаров для просмотра и
    context['all_items_complete'] - флаг, что все допустимы товары вывели
    """
    try:
        client = Client.objects.select_related('user').get(user=user)
        queryset_historyview = HistoryView.objects.prefetch_related('item_view').get(client=client)
        item_in_page_views_check = queryset_historyview.item_in_page_views_check()
        max_limit = queryset_historyview.limit_items_views

        list_item_views = queryset_historyview.item_view.all()[::-1][:item_in_page_views_check]
        if len(queryset_historyview.item_view.all()[:max_limit]) <= item_in_page_views_check:
            all_items_complete = False
        else:
            all_items_complete = True

    except BaseException:
        list_item_views = []
        all_items_complete = True

    return [list_item_views, all_items_complete]


def get_context_data_ajax(user, items_in_page) -> list:
    """
    Функция возвращает товары, которые нужно добавить на страницу просмотров
    """
    client = Client.objects.select_related('user').get(user=user)
    queryset_historyview = HistoryView.objects.prefetch_related('item_view').get(client=client)
    limit_items_views = queryset_historyview.limit_items_views
    item_in_page_views_check = queryset_historyview.item_in_page_views_check()
    list_item_views = queryset_historyview.item_view.all()[::-1][:limit_items_views]

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
        for i in item.productphoto_set.all()[:1]:
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

