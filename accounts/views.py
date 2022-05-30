from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str

from accounts.forms import RegistrationForm
from accounts.models import Client
from accounts.tasks import send_client_email_task


def registration_view(request):
    """
    Регистрация пользователя с отправкой письма активации
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            send_client_email_task.delay(
                user_id=user.id,
                site=current_site.domain,
                subject='Активация аккаунта',
                template='account_activation'
            )
            return render(request, 'accounts/registration_confirm.html')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/registration.html', {'form': form})


def account_activate(request, uidb64, token):
    """
    Берем из URL токен и id пользователя, проверяем на подлинность.
    Если всё ок, то создаем объект клиента, логиним и редиректим на главную.
    """
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = User.objects.filter(pk=uid).first()
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        Client.objects.create(user=user)
        login(request, user)
        return redirect('/')
    else:
        return HttpResponseNotFound('Ошибка, обратитесь в службу поддержки')