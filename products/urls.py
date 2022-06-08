from django.urls import path

from . import views


app_name = "products"

urlpatterns = [
    path("payment/", views.PaymentView.as_view(), name="payment"),
    path("add_goods/<int:pk>/", views.GoodsView.as_view(), name="add_goods"),
    path("discount/<int:pk>/", views.DiscountView.as_view(), name="discount"),
    path("historyview/", views.HistoryView.as_view(), name="history view"),
    path("comment/<int:pk>/", views.ProductComment.as_view(), name="product comment"),
    path("comparison/<int:pk>/", views.ProductComparison.as_view(), name="product comparison"),
    path("category/<int:pk>/", views.ProductListView.as_view(), name="product_list"),
    path('product_detail/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path("products/<int:pk>/", views.ProductTagListView.as_view(), name="product-tag")
]
