from abc import ABC, abstractmethod

from django.db import models
from django.db.models import QuerySet

from shops.models import ShopProduct


class AbstractDiscountedShopProductCond(ABC):
    @abstractmethod
    def condition(self) -> models.Q:
        """
        Возвращает условие фильтра для выбора товаров со скидкой.
        """
        pass


class AbstractDiscountedShopProductFilter(ABC):
    @abstractmethod
    def filter(self, queryset: QuerySet[ShopProduct],
               additional_cond: models.Q = None) -> QuerySet[ShopProduct]:
        """
        Фильтрует товары в соответствии с условием.
        """
        pass


class AbstractDiscountedShopProductFilterStrategy(AbstractDiscountedShopProductCond,
                                                  AbstractDiscountedShopProductFilter, ABC):
    """
    Интерфейс стратегии выбора товаров со скидкой.
    """

    def filter(self, queryset: QuerySet[ShopProduct],
               additional_cond: models.Q = None) -> QuerySet[ShopProduct]:
        """
        Фильтрует товары в соответствии с условием.
        """
        cond = self.condition()
        if additional_cond:
            cond = cond & additional_cond
        return queryset.filter(cond)


class PromoShopProductFilterStrategy(AbstractDiscountedShopProductFilterStrategy):
    """
    Выбор товаров со скидкой.
    """

    def condition(self) -> models.Q:
        return ~models.Q(promotion__isnull=True)


class PromoGroupShopProductFilterStrategy(AbstractDiscountedShopProductFilterStrategy):
    """
    Выбор товаров со скидкой, входящих в группу скидок.
    """

    def condition(self) -> models.Q:
        return ~models.Q(product__promotion_group__isnull=True)


class OnlyPromoGroupShopProductFilterStrategy(AbstractDiscountedShopProductFilterStrategy):
    """
    Выбор товаров со скидкой, входящих в группу скидок,
    но при этом на эти товары не назначена персональная скидка.
    """

    def condition(self) -> models.Q:
        return models.Q(promotion__isnull=True) & ~models.Q(product__promotion_group__isnull=True)


class PromoShopProductFilter(AbstractDiscountedShopProductFilter):
    """
    Выбирает товары со скидкой.
    """

    def __init__(self):
        self._strategy = None

    def _set_strategy(self, new_strategy):
        self._strategy = new_strategy

    strategy = property(fset=_set_strategy)

    def filter(self, queryset: QuerySet[ShopProduct],
               additional_cond: models.Q = None) -> QuerySet[ShopProduct]:
        """
        Фильтрует товары в соответствии с условием.
        """
        return self._strategy.filter(queryset, additional_cond=additional_cond)


class PromoShopProductStrategyFactory:
    """
    Фабрика стратегий фильтра товаров со скидкой.
    """

    @staticmethod
    def get_promo_shop_product_filter_strategy() -> PromoShopProductFilterStrategy:
        """
        Создает стратегию выбора товаров с персональной скидкой.
        """
        return PromoShopProductFilterStrategy()

    @staticmethod
    def get_promo_group_shop_product_filter_strategy() -> PromoGroupShopProductFilterStrategy:
        """
        Создает стратегию выбора товаров, входящих в группу товаров со скидкой.
        """
        return PromoGroupShopProductFilterStrategy()

    @staticmethod
    def get_only_promo_group_shop_product_filter_strategy() -> OnlyPromoGroupShopProductFilterStrategy:
        """
        Создает стратегию выбора товаров, входящих в группу товаров со скидкой,
        но на которые на назначена персональная скидка.
        """
        return OnlyPromoGroupShopProductFilterStrategy()


shop_product_filter = PromoShopProductFilter()
strategy_factory = PromoShopProductStrategyFactory()
