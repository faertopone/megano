from django.contrib import admin

from basket.models import BasketItem


@admin.register(BasketItem)
class BasketItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'client', 'product', 'qty', 'updated']
