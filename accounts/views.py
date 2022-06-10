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
from django.views.generic import DetailView, ListView, FormView, UpdateView

from .forms import RegistrationForm, ProfileEditForm
from .models import Client, HistoryView
from .services import initial_form_profile, post_context
from .tasks import send_client_email_task

from django.core import serializers


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
        return Client.objects.select_related('user').filter(user=self.request.user).first()

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        if self.request.user.is_superuser:
            return HttpResponseRedirect(('/admin/'))
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
            return HttpResponseRedirect(('/admin/'))

        initial_data = initial_form_profile(request=request)
        init_form = initial_data[0]
        client = initial_data[1]
        form = ProfileEditForm(initial=init_form)
        context = {'form': form,
                   'client': client,
                   'msg': messages}

        return render(request, 'accounts/profile_edit.html', context=context)

    def post(self, request, pk):
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
        client = Client.objects.select_related('user').get(user=self.request.user)
        list_item_views = HistoryView.objects.get(client=client).item_view.all()[::-1][:4]
        context['list_item_views'] = list_item_views
        return context

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        if self.request.user.is_superuser:
            return HttpResponseRedirect(('/admin/'))

        client = Client.objects.select_related('user').get(user=self.request.user)
        limit_items_views = HistoryView.objects.get(client=client).limit_items_views
        # Флаг, который говорит что все элементы передали и больше новых нет
        flag_items_complete = False

        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == 'POST':
            items_in_page = int(request.POST.get('add_item'))
            end_elemet = items_in_page + 4
            list_item_views = HistoryView.objects.get(client=client).item_view.all()[::-1][:limit_items_views]
            if end_elemet >= len(list_item_views):
                end_elemet = limit_items_views
                flag_items_complete = True
            list_item_views = list_item_views[items_in_page:end_elemet]
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

            # Преобразовываем все в json что бы отправить для ajax ( потому что там список queryset)
            product = serializers.serialize('json', list_item_views)
            return JsonResponse({'products': list_in_page,
                                 'count_product': items_in_page,
                                 'flag_items_complete': flag_items_complete,
                                 }, safe=False)

        return super().dispatch(request, *args, **kwargs)
