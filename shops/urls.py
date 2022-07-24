from django.urls import path

from .views import ShopDetailVew, ShopListView

urlpatterns = [
    path("", ShopListView.as_view(), name="shop-list"),
    path("<int:pk>/", ShopDetailVew.as_view(), name="shop-detail"),
]
