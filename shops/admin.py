from django.contrib import admin
from .models import Shops, ShopPhoto, Promotions, ShopUser, ShopProduct
from django.utils.translation import gettext_lazy as _


class ShopPhotoInline(admin.TabularInline):
    fk_name = 'shop'
    model = ShopPhoto


class ShopProductInline(admin.TabularInline):
    fk_name = 'shop'
    model = ShopProduct


class ShopUserInline(admin.TabularInline):
    fk_name = 'shop'
    model = ShopUser


class ShopsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'city', 'street', 'house_number',
                    'phone', 'email', 'rating', 'promotion']
    search_fields = ['name', 'city']
    list_filter = ['city']
    inlines = [ShopPhotoInline, ShopProductInline, ShopUserInline]

    def __str__(self):
        return _('профиль магазина')


class PromotionsAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'discount']
    search_fields = ['name']

    def __str__(self):
        return _('акции')


class ProductShopAdmin(admin.ModelAdmin):
    list_display = ['shop', 'product', 'amount', 'price_in_shop', 'promotion', 'special_price']
    search_fields = ['name']

    def __str__(self):
        return _('Товар в магазине')


admin.site.register(Shops, ShopsAdmin)
admin.site.register(ShopProduct, ProductShopAdmin)
admin.site.register(Promotions, PromotionsAdmin)
