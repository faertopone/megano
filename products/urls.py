from django.urls import path

from views import PaymentView, GoodsView, DiscountView

urlpatterns = [
    path("payment/", PaymentView.as_view(), name="payment"),
    path("add_goods/<int:pk>/", GoodsView.as_view(), name="add_goods"),
    path("discount/<int:pk>/", DiscountView.as_view(), name="discount")
]
