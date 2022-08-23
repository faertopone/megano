from typing import Union, Dict, Optional, List

from django.db.models import QuerySet

from shops.models import ShopProduct
from .models import Promotions
from promotions.utils.promo_filter import shop_product_filter, strategy_factory


class PromotionService:
    """
    Сервис скидок.
    """

    @staticmethod
    def _get_queryset(products: Union[ShopProduct, QuerySet[ShopProduct]]) -> QuerySet[ShopProduct]:
        if isinstance(products, QuerySet):
            return products.order_by("pk")
        return products.objects.all().order_by("pk")

    @staticmethod
    def _update_promotions(promotions: Dict[int, List[Promotions]], pk: int, promotion: Promotions):
        if pk in promotions:
            promotions[pk].append(promotion)
        else:
            promotions[pk] = [promotion]

    def get_all_product_promotions(self, product: ShopProduct) -> List[Promotions]:
        """
        Получить все скидки на указанный товар.

        :param product: Товар.
        :return: Список скидок.
        """
        promotions: List[Promotions] = []

        if product.promotion:
            # если на товар назначена скидка
            promotions.append(product.promotion)
        if product.product.promotion_group:
            # если товар входит в скидочную группу
            promotions.append(product.product.promotion_group.promotion)
        return promotions

    def get_all_promotions(self, products: Union[ShopProduct, QuerySet[ShopProduct]]) -> Dict[int, List[Promotions]]:
        """
        Получить все скидки на указанный список товаров.

        :param products: Товары в магазине.
        :return: Список скидок.
        """
        queryset = self._get_queryset(products)

        # получаем все товары со скидкой
        shop_product_filter.strategy = strategy_factory.get_promo_shop_product_filter_strategy()
        products_with_promo = shop_product_filter.filter(queryset)
        # получаем все товары, входящие в скидочную группу
        shop_product_filter.strategy = strategy_factory.get_promo_group_shop_product_filter_strategy()
        products_in_promo_group = shop_product_filter.filter(queryset)

        # объединяем скидки по полученным товарам в один список
        promotions = dict()
        for p in products_with_promo.all():
            self._update_promotions(promotions, p.pk, p.promotion)
        for p in products_in_promo_group.all():
            self._update_promotions(promotions, p.pk, p.product.promotion_group.promotion)

        return promotions

    def get_priority_product_promotion(self, product: ShopProduct) -> Optional[Promotions]:
        """
        Получить приоритетную скидку на указанный товар.

        :param product: Товар.
        :return: Приоритетная скидка.
        """
        if product.promotion:
            # если на товар назначена скидка
            return product.promotion
        elif product.product.promotion_group:
            # если товар входит в скидочную группу
            return product.product.promotion_group.promotion
        else:
            return None

    def get_priority_promotions(self, products: Union[ShopProduct, QuerySet[ShopProduct]]
                                ) -> Dict[int, Promotions]:
        """
        Получить приоритетную скидку на указанный список товаров.

        :param products: Товары в магазине.
        :return: Приоритетные скидки.
        """
        queryset = self._get_queryset(products)

        # получаем все товары со скидкой
        shop_product_filter.strategy = strategy_factory.get_promo_shop_product_filter_strategy()
        products_with_promo = shop_product_filter.filter(queryset)
        # получаем все товары, входящие в скидочную группу,
        # но у которых не назначена скидка
        shop_product_filter.strategy = strategy_factory.get_only_promo_group_shop_product_filter_strategy()
        products_in_promo_group = shop_product_filter.filter(queryset)

        # объединяем скидки по полученным товарам в один список
        promotions = dict()
        for p in products_with_promo.all():
            promotions[p.pk] = p.promotion
        for p in products_in_promo_group.all():
            promotions[p.pk] = p.product.promotion_group.promotion

        return promotions

    def get_basket_promotion(self, products: QuerySet[ShopProduct]) -> float:
        """
        Получить скидку на корзину.

        :param products: Товары в корзине.
        :return: Общая скидка по всем товарам, которую нужно вычесть из общей суммы
            корзины, чтобы получить итоговую стоимость.
        """
        promotions = self.get_priority_promotions(products)
        products = ShopProduct.objects.filter(pk__in=list(promotions.keys()))
        products = {p.pk: float(p.price_in_shop) for p in products}

        discount: float = 0
        for pk, promo in promotions.items():
            discount += products[pk] * promo.discount * 0.01

        return round(discount, 2)
