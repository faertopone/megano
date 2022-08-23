from django.urls import path

from .views import ShopListView, ShopProductListView

urlpatterns = [
    path("", ShopListView.as_view(), name="shop-list"),
    path("<int:pk>/", ShopProductListView.as_view(), name="shop-detail"),
]
