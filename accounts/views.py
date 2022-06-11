from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseNotFound, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.views import View
from django.views.generic import DetailView, ListView
from .forms import RegistrationForm, ProfileEditForm
from .models import Client, HistoryView
from .services import initial_form_profile, post_context, get_context_data, get_context_data_ajax
from .tasks import send_client_email_task


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


class ProfileView(ListView):
    model = Client
    context_object_name = 'client'
    template_name = 'accounts/profile.html'

    def get_queryset(self):
        return Client.objects.select_related('user').get(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['list_item_views'] = HistoryView.objects.get(client=self.get_queryset()).item_view.all()[::-1][:3]
        except BaseException:
            context['list_item_views'] = []
        return context

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        if self.request.user.is_superuser:
            return HttpResponseRedirect('/admin/')
        return super().dispatch(request, *args, **kwargs)


class ProfileEditView(View):
    """
    Класс редактирования личного кабинета пользователя
    """

    def get(self, request, pk):
        messages = ''
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        if self.request.user.is_superuser:
            return HttpResponseRedirect('/admin/')

        initial_data = initial_form_profile(request=request)
        init_form = initial_data[0]
        client = initial_data[1]
        form = ProfileEditForm(initial=init_form)
        context = {'form': form,
                   'client': client,
                   'msg': messages}

        return render(request, 'accounts/profile_edit.html', context=context)

    @staticmethod
    def post(request, pk):
        initial_data = initial_form_profile(request=request)
        init_form = initial_data[0]
        form = ProfileEditForm(request.POST, request.FILES, initial=init_form)
        context = post_context(request=request, form=form)

        return render(request, 'accounts/profile_edit.html', context=context)


class HistoryUserView(DetailView):
    """
    Класс вывода просмотренных товаров, пользователем
    """
    model = Client
    context_object_name = 'client'
    template_name = 'accounts/history_view.html'

    def get_queryset(self):
        return Client.objects.select_related('user').filter(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Функция сбора данных для первого вывода страницы
        data = get_context_data(user=self.request.user)
        context['list_item_views'] = data[0]
        context['all_items_complete'] = data[1]
        return context

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        if self.request.user.is_superuser:
            return HttpResponseRedirect('/admin/')

        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == 'POST':
            if request.POST.get('add_item'):
                data = get_context_data_ajax(user=self.request.user, items_in_page=int(request.POST.get('add_item')))
                list_in_page = data[0]
                flag_items_complete = data[1]
                return JsonResponse({'products': list_in_page,
                                     'flag_items_complete': flag_items_complete,
                                     }, safe=False)

        return super().dispatch(request, *args, **kwargs)
