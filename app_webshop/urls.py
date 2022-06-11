from django.urls import path

from app_webshop.views import Index

urlpatterns = [
    path('', Index.as_view(), name='index'),
]
