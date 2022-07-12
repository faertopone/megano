from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseNotFound, JsonResponse, \
    HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.views.generic import DetailView, ListView, FormView

from basket.models import BasketItem
from .forms import RegistrationForm, ProfileEditForm
from .models import Client
from .services import get_context_data, get_context_data_ajax, \
    initial_form_profile_new, save_dop_parametrs
from .tasks import send_client_email_task
from django.contrib.auth.views import LoginView
from django.contrib.auth import login


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


class ProfileView(LoginRequiredMixin, ListView):
    """
    Класс представления личного кабинета. Данные о пользователе
    """
    model = Client
    context_object_name = 'client'
    template_name = 'accounts/profile.html'
    redirect_field_name = None

    def get_queryset(self):
        return Client.objects.select_related('user').prefetch_related('item_view').get(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_item_views'] = self.get_queryset().item_view.all().order_by('-client_products_views__id')[:3]
        context['order_last'] = self.get_queryset().orders.first()
        return context


class ProfileEditView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    """
    Класс редактирования личного кабинета пользователя
    """
    template_name = 'accounts/profile_edit.html'
    form_class = ProfileEditForm
    success_message = 'Профиль успешно обновлен!'
    redirect_field_name = None

    def get_initial(self):
        return initial_form_profile_new(self.request)

    def get_context_data(self, **kwargs):
        context = super(ProfileEditView, self).get_context_data(**kwargs)
        context['client'] = Client.objects.select_related('user').prefetch_related('item_view').get(user=self.request.user)
        return context

    def form_valid(self, form):
        # Дополнительно сохраним изменения
        form.save(commit=False)
        save_dop_parametrs(request=self.request, form=form)
        return super().form_valid(form)

    def get_success_url(self):
        client = Client.objects.select_related('user').prefetch_related('item_view').get(user=self.request.user)
        return reverse('profile-edit', kwargs={'pk': client.pk})


class HistoryUserView(LoginRequiredMixin, DetailView):
    """
    Класс вывода просмотренных товаров, пользователем
    """

    context_object_name = 'client'
    template_name = 'accounts/history_view.html'
    redirect_field_name = None

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

        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == 'POST':
            if request.POST.get('add_item'):
                data = get_context_data_ajax(user=self.request.user, items_in_page=int(request.POST.get('add_item')))
                list_in_page = data[0]
                flag_items_complete = data[1]
                return JsonResponse({'products': list_in_page,
                                     'flag_items_complete': flag_items_complete,
                                     }, safe=False)

        return super().dispatch(request, *args, **kwargs)


class LogView(LoginView):
    template_name = 'accounts/login.html'
    form_class = AuthenticationForm

    def form_valid(self, form):
        """Копируем корзину из сессии в модель, если у клиента она пустая"""
        session_key = self.request.session.session_key
        user = form.get_user()
        login(self.request, user)

        client_basket = BasketItem.objects.filter(
            client=self.request.user.client
        )
        session_basket = BasketItem.objects.filter(session=session_key)
        if not client_basket and session_basket:
            for item in session_basket:
                item.client = self.request.user.client
                item.session = None
                item.save()
        return HttpResponseRedirect(self.get_success_url())
