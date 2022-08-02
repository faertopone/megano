from django.urls import path

from . import views, services


app_name = "products"

urlpatterns = [
    path("payment/", views.PaymentView.as_view(), name="payment"),
    path("add_goods/<int:pk>/", views.GoodsView.as_view(), name="add_goods"),
    path("discount/<int:pk>/", views.DiscountView.as_view(), name="discount"),
    path("comment/<int:pk>/", views.ProductComment.as_view(), name="product comment"),
    path("category/<int:pk>/", views.CategoryProductListView.as_view(), name="product_list"),
    path('product_detail/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path("products/<int:pk>/", views.ProductTagListView.as_view(), name="product-tag"),
    path("sale/<int:pk>/", views.PromotionProductListView.as_view(), name="product_sale"),
    path("sale_group/<int:pk>/", views.PromotionGroupProductListView.as_view(), name="product_sale_group"),
    path("comment/<int:pk>/", views.ProductComment.as_view(), name="product comment"),
    path("comparison/", views.ProductCompareView.as_view(), name="product-comparison"),
    path("category/<int:pk>/", views.CategoryProductListView.as_view(), name="product_list"),
    path('product_detail/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path("products/<int:pk>/", views.ProductTagListView.as_view(), name="product-tag"),
    path("count_compare_add/", services.count_compare_add, name="count-compare-add"),
    path('lazy_load_reviews/', views.lazy_load_reviews_views, name='lazy_load_reviews'),
    path("sale/<int:pk>/", views.PromotionProductListView.as_view(), name="product_sale"),
    path("sale_group/<int:pk>/", views.PromotionGroupProductListView.as_view(), name="product_sale_group"),
    path("search/", views.SearchedProductListView.as_view(), name="product_search"),
]
