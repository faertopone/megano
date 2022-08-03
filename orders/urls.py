from django.urls import path
from orders.views import OrderDetailView, OrderProgressView, OrderListView, OrderPayment

urlpatterns = [
    path('order_list/', OrderListView.as_view(), name='orders'),
    path('order/<int:pk>', OrderDetailView.as_view(), name='order-detail'),
    path('orders_progress/', OrderProgressView.as_view(), name='order-progress'),
    path('orders_payment/<int:pk>', OrderPayment.as_view(), name='payment'),
]
