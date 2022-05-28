from django.contrib import admin
from accounts.models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_seller']
    list_filter = ['is_seller']
