from django.urls import path, include
from banners.views import Index

urlpatterns = [
    path('', Index.as_view(), name='index'),
]