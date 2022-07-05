from django.urls import path

from . import views, services


app_name = "products"

urlpatterns = [
    path("payment/", views.PaymentView.as_view(), name="payment"),
    path("add_goods/<int:pk>/", views.GoodsView.as_view(), name="add_goods"),
    path("discount/<int:pk>/", views.DiscountView.as_view(), name="discount"),
    path("historyview/", views.HistoryView.as_view(), name="history view"),
    path("comparison/", views.ProductCompareView.as_view(), name="product-comparison"),
    path("category/<int:pk>/", views.ProductListView.as_view(), name="product_list"),
    path('product_detail/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path("products/<int:pk>/", views.ProductTagListView.as_view(), name="product-tag"),
    path("count_compare_add/", services.count_compare_add, name="count-compare-add"),
    path('lazy_load_reviews/', views.lazy_load_reviews_views, name='lazy_load_reviews'),
]
