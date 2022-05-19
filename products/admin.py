from django.contrib import admin  # noqa: F401
from django.contrib.admin import TabularInline
from django.db.models import QuerySet
from django.http import HttpRequest
from django.template.defaultfilters import truncatewords
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Category, Product, Property, PropertyProduct


# inlines
class PropertyProductInline(TabularInline):
    model = PropertyProduct
    extra = 0


# admins
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display, list_display_links = (
         ("category_name", "activity", "icon_photo_view", "description_view"),
    ) * 2

    list_filter = ("activity",)
    search_fields = ("category_name", "description")

    actions = ("activate_categories", "deactivate_categories")

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
        return format_html(
            '<span title="{}">{}</span>'.format(
                obj.description,
                truncatewords(obj.description, 15)
            )
        )

    @admin.display(description=_("Активировать выбранные категории"))
    def activate_categories(self, request: HttpRequest, queryset: QuerySet):
        """
        Активирует выбранные категории.
        """
        updated = queryset.update(activity=True)
        self.message_user(request, f"Активировано {updated} категорий")

    @admin.display(description=_("Деактивировать выбранные категории"))
    def deactivate_categories(self, request: HttpRequest, queryset: QuerySet):
        """
        Деактивирует выбранные категории.
        """
        updated = queryset.update(activity=False)
        self.message_user(request, f"Деактивировано {updated} категорий")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "article", "category_view", "price",
                    "rating_view", "flag_limit", "property_count_view")
    list_display_links = ("name", "article")
    list_editable = ("price",)

    list_filter = ("flag_limit", "category__category_name")
    search_fields = ("name", "article")

    readonly_fields = ("rating",)

    inlines = (PropertyProductInline,)

    fieldsets = (
        (None, {
            "fields": ("name", "article", "category")
        }),
        ("Склад", {
            "fields": ("price", "flag_limit")
        }),
    )

    @staticmethod
    @admin.display(description=_("Категория каталога"))
    def category_view(obj: Product):
        """
        Выводит ссылку на категорию каталога
        """
        return format_html(
            '<a href="{}?pk={}">{}</a>',
            reverse("admin:products_category_changelist"),
            obj.category.pk,
            obj.category.category_name
        )

    @staticmethod
    @admin.display(description=_("Рэйтинг"))
    def rating_view(obj: Product):
        """
        Выводит рейтинг
        """
        if obj.rating <= 100:
            color = "red"
        elif 100 < obj.rating <= 1000:
            color = "yellow"
        elif obj.rating > 1000:
            color = "green"

        return format_html(
            '''<div style="text-align: center;">
                    <img src="https://img.shields.io/badge/{message}-{rating}-{color}" alt="{rating}" />
               </div>'''.format(message=_("рейтинг"), rating=obj.rating, color=color)
        )

    @staticmethod
    @admin.display(description=_("Количество свойств"))
    def property_count_view(obj: Product):
        return obj.properties.count()


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("name", "tooltip_view")
    list_display_links = ("name",)

    search_fields = ("name", "tooltip")

    @staticmethod
    @admin.display(description="Примечание")
    def tooltip_view(obj: Property):
        return format_html(
            '<span title="{}">{}</span>'.format(
                obj.tooltip,
                truncatewords(obj.tooltip, 15)
            )
        )
