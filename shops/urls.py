from django.urls import path

from .views import ShopDetailVew

urlpatterns = [
    path("<int:pk>/", ShopDetailVew.as_view(), name="shop detail"),
]
