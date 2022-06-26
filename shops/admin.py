from django.contrib import admin
from .models import Shops, ShopPhoto, Promotions, ShopUser, ShopProduct, PromotionGroup
from django.utils.translation import gettext_lazy as _


class ShopPhotoInline(admin.TabularInline):
    fk_name = 'shop'
    model = ShopPhoto
    extra = 0


class ShopProductInline(admin.TabularInline):
    fk_name = 'shop'
    model = ShopProduct
    extra = 0


class ShopUserInline(admin.TabularInline):
    fk_name = 'shop'
    model = ShopUser
    extra = 0


class ShopsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'city', 'street', 'house_number',
                    'phone', 'email', 'rating', 'promotion']
    search_fields = ['name', 'city']
    list_filter = ['city']
    inlines = [ShopPhotoInline, ShopProductInline, ShopUserInline]

    def __str__(self):
        return _('shop profile')


class PromotionsAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'discount']
    search_fields = ['name']

    def __str__(self):
        return _('name')


class ProductShopAdmin(admin.ModelAdmin):
    list_display = ['shop', 'product', 'amount', 'price_in_shop', 'promotion', 'special_price',
                    'promotion_group']
    search_fields = ['name']

    def __str__(self):
        return _('product__name')


class PromotionGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "promotion")
    list_display_links = ("name",)

    search_fields = ("name",)
    list_filter = ("promotion",)


admin.site.register(Shops, ShopsAdmin)
admin.site.register(ShopProduct, ProductShopAdmin)
admin.site.register(Promotions, PromotionsAdmin)
admin.site.register(PromotionGroup, PromotionGroupAdmin)
