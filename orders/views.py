from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DetailView, FormView, ListView

from accounts.models import Client
from basket.models import BasketItem
from orders.forms import OrderForm
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
    redirect_field_name = None

    def get_initial(self):
        return initial_order_form(request=self.request)

    def get_context_data(self, **kwargs):
        context = super(OrderProgressView, self).get_context_data(**kwargs)
        client = Client.objects.select_related('user').prefetch_related('item_view', 'orders').get(
            user=self.request.user)
        total_basket = BasketItem.objects.filter(client=client).aggregate(price_sum=Sum(F('price') * F('qty')))
        context['client'] = client
        context['item_in_basket'] = BasketItem.objects.filter(client=client)
        context['total_price'] = total_basket.get('price_sum')
        return context

    def form_valid(self, form):
        # Дополнительно сохраним изменения
        order = form.save()
        order_service(order=order, user=self.request.user)
        # Этот id заказа потом передадим в ссылку перенаправления
        self.order = order.id
        self.pay_method = order.payment
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == 'POST':
            # ================= ТУТ ЗНАЧЕНИЯ ИЗ МОДЕЛИ СКИДОК
            price_delivery = 500
            freed_delivery = 200
            return JsonResponse({'price_delivery': price_delivery,
                                 'freed_delivery': freed_delivery})

        client = Client.objects.select_related('user').prefetch_related('item_view').get(user=self.request.user)
        order = BasketItem.objects.filter(client=client)
        if not order:
            return HttpResponseRedirect(reverse('index'))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.pay_method == 'Онлайн картой':
            pass

        return HttpResponseRedirect(reverse('index'))


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
