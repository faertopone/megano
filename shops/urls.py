from django.urls import path

from .views import shop_info

urlpatterns = [
    path("<int:pk>/", shop_info, name="shop detail"),
]
