from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, FormView, ListView, CreateView

from accounts.models import Client
from orders.forms import OrderForm
from orders.models import Order


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    context_object_name = 'order'
    template_name = '??'
    redirect_field_name = None


class OrderProgressView(LoginRequiredMixin, FormView):
    context_object_name = 'order'
    form_class = OrderForm
    template_name = '??'
    redirect_field_name = None

    def form_valid(self, form):
        # Дополнительно сохраним изменения
        form.save()
        order = Order.objects.create(**form.cleaned_data)
        client = Client.objects.select_related('user').prefetch_related('item_view').get(user=self.request.user)
        client.orders.add(order)
        return super().form_valid(form)


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    context_object_name = 'order_list'
    template_name = '??'
    redirect_field_name = None