from django.urls import path

from .views import PaymentView, GoodsView, DiscountView, HistoryView, \
                   ProductComment, ProductComparison, product_detail_review, ProductListView


app_name = "products"

urlpatterns = [
    path("payment/", PaymentView.as_view(), name="payment"),
    path("add_goods/<int:pk>/", GoodsView.as_view(), name="add_goods"),
    path("discount/<int:pk>/", DiscountView.as_view(), name="discount"),
    path("historyview/", HistoryView.as_view(), name="history view"),
    path("comment/<int:pk>/", ProductComment.as_view(), name="product comment"),
    path("review/<int:pk>/", product_detail_review, name="product review"),
    path("comparison/<int:pk>/", ProductComparison.as_view(), name="product comparison"),
    path("category/<int:pk>", ProductListView.as_view(), name="product_list"),
]
