from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from orders.models import DeliverySetting


@admin.register(DeliverySetting)
class DeliverySettingAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'express_delivery_price', 'delivery_price', 'is_active')
    list_display_links = ('name', 'id', )
    list_editable = ('express_delivery_price', 'delivery_price')
    list_filter = ['name', 'is_active']
    actions = ['active', 'not_active']
    # Поиск по имени и совпадение с началом слова типа startswith
    search_fields = ['^name', ]

    @admin.display(description=_("включить"))
    def active(self, request: HttpRequest, queryset: QuerySet):
        """
        Активирует выбранный способ доставки
        """
        update = queryset.update(is_active=True)
        self.message_user(request, f'Активирован {update} способ!')

    @admin.display(description=_("отключить"))
    def not_active(self, request: HttpRequest, queryset: QuerySet):
        """
        Отключает выбранный способ доставки
        """
        update = queryset.update(is_active=False)
        self.message_user(request, f'Выключен {update} способ!')