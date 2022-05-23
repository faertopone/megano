from django.contrib import admin
from .models import Shops, ShopPhoto, Promotions, ShopUser
from django.utils.translation import gettext_lazy as _


class ShopPhotoInline(admin.TabularInline):
    fk_name = 'shop'
    model = ShopPhoto


class ShopUserInline(admin.TabularInline):
    fk_name = 'shop'
    model = ShopUser


class ShopsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'city', 'street', 'house_number',
                    'phone', 'email', 'rating', 'promotion']
    search_fields = ['name', 'city']
    list_filter = ['city']
    inlines = [ShopPhotoInline, ShopUserInline]

    def __str__(self):
        return _('shop profile')


class PromotionsAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'discount']
    search_fields = ['name']

    def __str__(self):
        return _('name')


admin.site.register(Shops, ShopsAdmin)
admin.site.register(Promotions, PromotionsAdmin)
