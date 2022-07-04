from django.urls import path
from basket.views import basket_add, basket_page, basket_delete


urlpatterns = [
    path('add/', basket_add, name='basket_add'),
    path('', basket_page, name='basket_page'),
    path('delete/', basket_delete, name='basket_delete')
]