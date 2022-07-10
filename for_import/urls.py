from django.urls import path
from .services import update_product_list, list_prop_category, export_file_csv


urlpatterns = [
	path('products/', update_product_list, name='import-product'),
	path("ajax/", list_prop_category),
	path('export/<int:pk>', export_file_csv, name='export-file'),
]
