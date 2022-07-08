from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView, FormView, ListView
from accounts.models import Client
from basket.models import BasketItem
from orders.forms import OrderForm, OrderPay
from orders.models import Order, DeliverySetting
from orders.services import initial_order_form, OrderService, PaymentService


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
    order_service = OrderService()

    def get_initial(self):
        return initial_order_form(request=self.request)

    def setup(self, request, *args, **kwargs):
        """
        Проверка, что в БД есть модель DeliverySetting - и инициализируем параметры от корзины
        """
        super().setup(request, *args, **kwargs)
        if not DeliverySetting.objects.all().exists():
            DeliverySetting.objects.create(name='Настройка  цен доставки')
        self.order_service.check_basket(request=self.request)
        self.order_service.check_free_delivery()

    def get_context_data(self, **kwargs):
        context = super(OrderProgressView, self).get_context_data(**kwargs)
        context['client'] = self.order_service.client
        context['item_in_basket'] = self.order_service.basket
        context['total_price'] = self.order_service.total_basket_price
        return context

    def form_valid(self, form):
        order = form.save()
        self.order_service.order_copy_data(order=order)
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):

        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.method == 'POST':
            return JsonResponse({'express_delivery_price': self.order_service.get_express_delivery_price(),
                                 'delivery_price': self.order_service.get_delivery_price(),
                                 'check_free_delivery': self.order_service.check_free_delivery()
                                 })

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('payment', kwargs={'pk': self.order_service.new_order_id})


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
    payment_service = PaymentService()

    def get_queryset(self):
        return self.payment_service.get_current_order(Order.objects.filter(pk=self.kwargs['pk']))

    def form_valid(self, form):
        self.payment_service.add_visa_in_order(form)
        self.payment_service.complete_payment()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('order-detail', kwargs={'pk': self.kwargs['pk']})


