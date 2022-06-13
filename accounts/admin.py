from django.contrib import admin
from accounts.models import Client
from django.utils.translation import gettext_lazy as _


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'is_seller', 'limit_items_views', 'item_in_page_views']
    list_filter = ['is_seller']
    list_display_links = ['user']
    search_fields = ['^name', ]
    autocomplete_fields = ['item_view']
    list_editable = ['limit_items_views', 'item_in_page_views']
