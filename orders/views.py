from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DetailView, FormView, ListView
from accounts.models import Client
from basket.models import BasketItem, BasketQuerySet, BasketManager
from orders.forms import OrderForm, OrderPay
from orders.models import Order
from orders.services import initial_order_form, order_service


class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    Детальная страница отображение заказа, с возможностью его оплатить, если еще не оплачен
    """

    context_object_name = 'order'
    template_name = 'orders/order_detail.html'

    def get_queryset(self):
        return Order.objects.filter(pk=self.kwargs['pk'])


class OrderProgressView(LoginRequiredMixin, FormView):
    """
    Создание заказа, с проверкой, если товаров в модели нет - перенаправит на главную страницу
    """
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
        order = form.save()
        order_service(order=order, user=self.request.user)
        # Этот id заказа потом передадим в ссылку перенаправления
        self.order = order.id
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            client = Client.objects.select_related('user').prefetch_related('item_view').get(user=self.request.user)
            order = BasketItem.objects.filter(client=client)
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == 'POST':
                # ================= ТУТ ЗНАЧЕНИЯ ИЗ МОДЕЛИ СКИДОК
                price_delivery = 500
                freed_delivery = 200
                return JsonResponse({'price_delivery': price_delivery,
                                     'freed_delivery': freed_delivery})
            if not order:
                return HttpResponseRedirect(reverse('index'))

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('payment', kwargs={'pk': self.order})


class OrderListView(LoginRequiredMixin, ListView):
    """
    Вывод списка заказов клиента
    """

    context_object_name = 'order_list'
    template_name = 'orders/order_list.html'

    def get_queryset(self):
        client = Client.objects.select_related('user').prefetch_related('item_view', 'orders').get(
            user=self.request.user)
        return client.orders.all()

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        client = Client.objects.select_related('user').prefetch_related('item_view', 'orders').get(
            user=self.request.user)
        contex['client'] = client
        return contex


class OrderPayment(LoginRequiredMixin, DetailView, FormView):
    form_class = OrderPay
    context_object_name = 'order'
    template_name = 'orders/order_payment.html'

    def get_queryset(self):
        return Order.objects.filter(pk=self.kwargs['pk'])

    def form_valid(self, form):
        # Просто статус ставлю ОПЛАЧЕНО
        order = self.get_queryset()[0]
        order.number_visa = form.cleaned_data.get('number_visa')
        order.status_pay = True
        order.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('order-detail', kwargs={'pk': self.kwargs['pk']})
