from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DetailView, FormView, ListView

from accounts.models import Client
from basket.models import BasketItem
from orders.forms import OrderForm
from orders.models import Order
from orders.services import initial_order_form


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    context_object_name = 'order'
    template_name = '??'
    redirect_field_name = None


class OrderProgressView(LoginRequiredMixin, FormView):
    """
    Создание заказа, с проверкой, если товаров в модели нет - перенаправит на главную страницу
    """
    context_object_name = 'order'
    form_class = OrderForm
    template_name = 'orders/order_progress.html'

    def get_initial(self):
        return initial_order_form(request=self.request)

    def get_context_data(self, **kwargs):
        context = super(OrderProgressView, self).get_context_data(**kwargs)
        client = Client.objects.select_related('user').prefetch_related('item_view', 'orders').get(
            user=self.request.user)
        context['client'] = client
        context['item_in_basket'] = BasketItem.objects.filter(client=client)
        return context

    def form_valid(self, form):
        # Дополнительно сохраним изменения
        form.save(commit=False)
        order = Order.objects.create(**form.cleaned_data)
        # Этот id заказа потом передадим в ссылку перенаправления
        self.order_id = order.id
        client = Client.objects.select_related('user').prefetch_related('item_view').get(user=self.request.user)
        client.orders.add(order)
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        client = Client.objects.select_related('user').prefetch_related('item_view').get(user=self.request.user)
        order = BasketItem.objects.filter(client=client)
        if not order:
            return HttpResponseRedirect(reverse('index'))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        print(self.order_id)
        return super(OrderProgressView, self).get_success_url()


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    context_object_name = 'order_list'
    template_name = '??'
    redirect_field_name = None