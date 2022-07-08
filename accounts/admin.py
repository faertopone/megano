from django.contrib import admin
from django.contrib.admin import TabularInline
from django.utils.safestring import mark_safe

from accounts.models import Client
from django.utils.translation import gettext_lazy as _

from orders.models import Order
from products.models import Category


class OrderInlines(admin.TabularInline):
    model = Order



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('number_order', 'total_price', 'transaction', 'email', 'status_pay', 'delivery_price', 'created_dt')
    list_display_links = ('number_order', 'email', )
    list_filter = ['number_order', 'total_price', 'status_pay', 'delivery_price', 'created_dt']
    actions = ['active', 'not_active']
    readonly_fields = ('first_name', 'last_name', 'patronymic', 'delivery', 'city', 'address', 'payment',
                       'total_price', 'status_pay', 'transaction', 'number_visa', 'email', 'number_order','phone',
                       'delivery_price', 'order_products', 'need_pay', 'created_dt')
    # Поиск по имени и совпадение с началом слова типа startswith
    search_fields = ['^name', ]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'is_seller', 'limit_items_views', 'item_in_page_views', 'get_orders_count', 'client_photo']
    list_filter = ['is_seller']
    list_display_links = ['user']
    search_fields = ['^name', ]
    autocomplete_fields = ['item_view']
    list_editable = ['limit_items_views', 'item_in_page_views']

    fieldsets = (
        (_('Основные параметры пользователя'), {
            'fields': ('user', 'phone', 'city'),
        }),
        (_('Фотография'), {
            'fields': (('photo',),)
        }),
        (_('История операций'), {
            'fields': ('spent_money',)
        }),
        (_('Какой статус на сайте'), {
            'fields': ('is_seller',)
        }),

    )

    @admin.display(description=_("Количество заказов"))
    def get_orders_count(self, obj: Client):
        orders = obj.orders.count()
        return orders

    @staticmethod
    @admin.display(description=_('Аватарка'))
    def client_photo(obj: Client):
        if not obj.photo:
            return 'Нету фотографии'
        return mark_safe('<img src="{}" width="50" height="50" />'.format(obj.photo.url))
