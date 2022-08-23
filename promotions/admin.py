from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Promotions, PromotionGroup


class PromotionsAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'discount']
    search_fields = ['name']

    def __str__(self):
        return _('name')


class PromotionGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "promotion", )
    list_display_links = ("name",)

    search_fields = ("name",)
    list_filter = ("promotion",)


admin.site.register(Promotions, PromotionsAdmin)
admin.site.register(PromotionGroup, PromotionGroupAdmin)
