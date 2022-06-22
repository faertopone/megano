from django.http import HttpRequest
from django.core.cache import cache

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


def getting_compare_info(request):
    """Возвращаут все данные этой функции"""
    session_key = request.session.session_key
    count_product_compare = 0
    if not session_key:
        request.session.cycle_key()
    if cache.get(str(session_key) + '_compare_count'):
        count_product_compare = cache.get(str(session_key) + '_compare_count')

    return locals()
