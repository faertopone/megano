from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from promotions.models import PromotionsShowProduct


@admin.register(PromotionsShowProduct)
class PromotionsShowProductAdmin(admin.ModelAdmin):
    list_display = ['product_show', 'limit_day_show_product', ]
    list_display_links = ['product_show', ]
    list_editable = ['limit_day_show_product']
    search_fields = ['name_product']
    autocomplete_fields = ['product_show']

    def name_product(self, obj: PromotionsShowProduct):
        return obj.product_show.name

