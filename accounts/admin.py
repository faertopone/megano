from django.contrib import admin
from accounts.models import Client, HistoryView
from django.utils.translation import gettext_lazy as _

class HistoryReviewInline(admin.TabularInline):
    model = HistoryView


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_seller']
    list_filter = ['is_seller']
    inlines = [HistoryReviewInline, ]


@admin.register(HistoryView)
class HistoryViewAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_username', 'limit_items_views', 'get_username']
    search_fields = ['^name',]
    list_display_links = ['get_username']
    autocomplete_fields = ['item_view']
    list_editable = ("limit_items_views",)
    readonly_fields = ("client",)
    fieldsets = (
        ('Товары, которые смотрел пользователь', {
            "fields": ("item_view", )
        }),
        ("Для пользователя ", {
            "fields": ("client", )
        }),
    )

    @staticmethod
    @admin.display(description=_('Пользователи'))
    def get_username(obj: HistoryView):
        return f'Пользователь {obj.client.user.username}'

    def __str__(self):
        return _('История просмотров')




