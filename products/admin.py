from django.contrib import admin  # noqa: F401
from django.template.defaultfilters import truncatewords
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display, list_display_links = (
         ("category_name", "activity", "icon_photo_view", "description_view"),
    ) * 2
    list_filter = ("activity",)
    ordering = ("category_name",)

    @staticmethod
    @admin.display(description=_("Иконка категории"))
    def icon_photo_view(obj: Category) -> str:
        return format_html(
            '<img src="{}" alt="{}" />',
            obj.icon_photo.url,
            obj.category_name,
        )

    @staticmethod
    @admin.display(description=_("Описание"))
    def description_view(obj: Category) -> str:
        return truncatewords(obj.description, 15)
