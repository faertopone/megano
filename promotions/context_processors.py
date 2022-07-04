from django.http import HttpRequest

from .services import PromotionService


def promotion_service(request: HttpRequest) -> dict:
    """
    Добавляет сервис скидок в контекст шаблона.
    """
    return {
        "promotion_service": PromotionService(),
    }
