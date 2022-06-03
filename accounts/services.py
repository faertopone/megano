from django.contrib.auth.models import User
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings

from accounts.forms import ProfileEditForm
from accounts.models import Client


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


def initial_form_profile(pk: int) -> list:
    """
    Функция инициализирует начальные значения Профиля
    """
    client = Client.objects.select_related('user').get(pk=pk)
    initial_client = {
        'phone': client.phone,
        'email': client.user.email,
        'family_name_lastname': client.family_name_lastname,
    }
    return [initial_client, client]


def get_context(request: HttpRequest, pk: int) -> object:
    """
    Представления Профиля при запросе GET
    """
    user = request.user
    initial_data = initial_form_profile(pk=pk)
    form = ProfileEditForm(instance=user, initial=initial_data[0])
    context = {'form': form,
               'client': initial_data[1]}
    return context


def post_context(request: HttpRequest, pk: int) -> object:
    """
     Представления Профиля при запросе POST и изменения данных, которые были изменены
     """
    user = request.user
    initial_data_all = initial_form_profile(pk=pk)
    initial_data = initial_data_all[0]
    client = initial_data_all[1]
    form = ProfileEditForm(request.POST, request.FILES, instance=user, initial=initial_data)
    if form.is_valid():
        # Если изменения были в форме, то выполним это
        if form.has_changed():
            form.save(commit=False)
            # Список какие поля были изменены
            change_data_list = form.changed_data
            # Извлечем данные с формы
            avatar = form.cleaned_data.get('photo')
            phone = form.cleaned_data.get('phone')
            email = form.cleaned_data.get('email')
            family_name_lastname = form.cleaned_data.get('family_name_lastname')
            password = form.cleaned_data.get('password1')

            if 'photo' in change_data_list:
                client.photo = avatar
            if 'phone' in change_data_list:
                client.phone = phone
            if 'email' in change_data_list:
                client.user.email = email
            if 'family_name_lastname' in change_data_list:
                client.family_name_lastname = family_name_lastname
            if 'password1' in change_data_list:
                client.user.set_password(password)

            client.save()
            client.user.save()

    context = {'form': form,
               'client': client}
    return context