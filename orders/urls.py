from django.urls import path
from orders.views import OrderDetailView, OrderProgressView, OrderListView

urlpatterns = [
    path('order/', OrderListView.as_view(), name='orders'),
    path('order/<int:pk>', OrderDetailView.as_view(), name='order-detail'),
    path('orders_progress/', OrderProgressView.as_view(), name='order-progress'),

    ]