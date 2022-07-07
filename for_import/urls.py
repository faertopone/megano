from django.urls import path
from .services import update_product_list, list_prop_category


urlpatterns = [
	path('products/', update_product_list, name='import-product'),
	path("ajax/", list_prop_category),
]
