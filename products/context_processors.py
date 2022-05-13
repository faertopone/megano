from django.http import HttpRequest

from .models import Category


def main_menu_categories(request: HttpRequest) -> dict:
    """
    Добавляет активные категории каталога в контекст шаблона.
    """
    active_categories = Category.objects.only("category_name", "icon_photo") \
        .filter(activity=True).order_by("category_name")
    return {
        "active_categories": active_categories,
    }
