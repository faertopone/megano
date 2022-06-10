from django.contrib.auth.models import User
from django.core import serializers
from django.http import HttpRequest, JsonResponse
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
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


def add_product_in_history(product: object, client: object):
    """
    Функция, добавляет просмотренный товар в БД
    """
    pass

def add_product_in_history_session(request: HttpRequest):
    """
    Функция, добавляет просмотренный товар сессию пользователя
    """
    pass