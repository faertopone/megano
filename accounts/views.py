from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.views import View

from accounts.forms import RegistrationForm, ProfileEditForm
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


class ProfileView(View):
    """
    Класс личного кабинета пользователя, который авторизован, и не является суперпользователем.
    """

    def get(self, request):
        user_info = request.user
        # Проверим, что пользователь авторизован и не супер пользователь
        if user_info.is_authenticated and not user_info.is_superuser:
            client = Client.objects.select_related('user').get(user=user_info)
        else:
            return HttpResponseRedirect(reverse('login'))

        context = {'client': client}

        return render(request, 'accounts/profile.html', context=context)


class ProfileEditView(View):
    """
    Класс редактирования личного кабинета пользователя
    """

    def get(self, request, pk):
        client = Client.objects.select_related('user').get(pk=pk)
        FIO = client.user.first_name + ' ' + str(client.family) + ' ' + client.user.last_name
        initial_client = {
            'phone': client.phone,
            'email': client.user.email,
            'FIO': FIO,
            'id_client': str(request.user.id)
        }
        form = ProfileEditForm(initial=initial_client)
        context = {'client': client,
                   'form': form,
                   }
        return render(request, 'accounts/profile_edit.html', context=context)

    def post(self, request, pk):
        client = Client.objects.select_related('user').get(pk=pk)
        FIO = client.user.first_name + ' ' + str(client.family) + ' ' + client.user.last_name
        initial_client = {
            'phone': client.phone,
            'email': client.user.email,
            'FIO': FIO,
            'id_client': str(request.user.id)
        }
        form = ProfileEditForm(request.POST, request.FILES, initial=initial_client)
        if form.is_valid():
            avatar = form.cleaned_data.get('photo')
            phone = form.cleaned_data.get('phone')
            email = form.cleaned_data.get('email')
            FIO = form.cleaned_data.get('FIO')
            password = form.cleaned_data.get('password1')

            #Логика как из строки ФИО раскидать по нужным параметрам данные
            FIO = FIO.split()
            if len(FIO) == 0:
                first_name = ''
                name = ''
                last_name = ''
            elif len(FIO) == 1:
                first_name = FIO[0]
                name = ''
                last_name = ''
            elif len(FIO) == 2:
                first_name = FIO[0]
                name = FIO[1]
                last_name = ''
            elif len(FIO) == 3:
                first_name = FIO[0]
                name = FIO[1]
                last_name = FIO[2]
            else:
                first_name = FIO[0]
                name = FIO[1]
                long_name = ''
                for i in range(2, len(FIO)):
                    long_name += FIO[i] + ' '
                last_name = long_name

            if avatar:
                client.photo = avatar
            client.phone = phone
            client.user.first_name = first_name
            client.family = name
            client.user.last_name = last_name
            client.user.email = email
            if password:
                client.user.set_password(password)
            client.user.save()
            client.save()

            messages.success(request, 'Настройки успешно обновлены!')

        context = {'form': form,
                   'client': client}


        return render(request, 'accounts/profile_edit.html', context=context)

