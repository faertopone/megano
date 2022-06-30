from typing import Union, Dict, Optional, List

from django.db import models
from django.db.models import QuerySet

from shops.models import ShopProduct
from .models import Promotions


class PromotionService:
    """
    Сервис скидок.
    """

    @staticmethod
    def _get_queryset(products: Union[ShopProduct, QuerySet]):
        if isinstance(products, QuerySet):
            return products.order_by("pk")
        return products.objects.all().order_by("pk")

    @staticmethod
    def _update_promotions(promotions: Dict[int, List[Promotions]], pk: int, promotion: Promotions):
        if pk in promotions:
            promotions[pk].append(promotion)
        else:
            promotions[pk] = [promotion]

    def get_all_promotions(self, products: Union[ShopProduct, QuerySet], pk=None) -> Dict[int, List[Promotions]]:
        """
        Получить все скидки на указанный список товаров или на один товар.

        :param products: Товары в магазине.
        :param pk: Если None, то вернет список скидок на все товары, иначе - на один товар.
        :return: Список скидок.
        """
        queryset = self._get_queryset(products)

        if pk is None:
            # получаем все товары со скидкой
            products_with_promo = queryset.filter(~models.Q(promotion__isnull=True))
            # получаем все товары, входящие в скидочную группу
            products_in_promo_group = queryset.filter(~models.Q(product__promotion_group__isnull=True))

            # объединяем скидки по полученным товарам в один список
            promotions = dict()
            for p in products_with_promo.all():
                self._update_promotions(promotions, p.pk, p.promotion)
            for p in products_in_promo_group.all():
                self._update_promotions(promotions, p.pk, p.product.promotion_group.promotion)

            return promotions
        else:
            promotions: Dict[int, List[Promotions]] = dict()

            try:
                product = queryset.get(pk=pk)
            except ShopProduct.DoesNotExist:
                promotions.clear()
                return promotions

            if product.promotion:
                # если на товар назначена скидка
                self._update_promotions(promotions, product.pk, product.promotion)
            if product.product.promotion_group:
                # если товар входит в скидочную группу
                self._update_promotions(promotions, product.pk, product.product.promotion_group.promotion)
            return promotions

    def get_priority_promotions(self, products: Union[ShopProduct, QuerySet],
                                pk=None) -> Union[Dict[int, List[Promotions]], Optional[Promotions]]:
        """
        Получить приоритетную скидку на указанный список товаров или на один товар.

        :param products: Товары в магазине.
        :param pk: Если None, то вернет список скидок, иначе - одну скидку.
        :return: Список скидок или одна скидка.
        """
        queryset = self._get_queryset(products)

        if pk is None:
            # получаем все товары со скидкой
            products_with_promo = queryset.filter(~models.Q(promotion__isnull=True))
            # получаем все товары, входящие в скидочную группу,
            # но у которых не назначена скидка
            products_in_promo_group = queryset.filter(
                models.Q(promotion__isnull=True) & ~models.Q(product__promotion_group__isnull=True)
            )

            # объединяем скидки по полученным товарам в один список
            promotions = dict()
            for p in products_with_promo.all():
                self._update_promotions(promotions, p.pk, p.promotion)
            for p in products_in_promo_group.all():
                self._update_promotions(promotions, p.pk, p.product.promotion_group.promotion)

            return promotions
        else:
            try:
                product = queryset.get(pk=pk)
            except ShopProduct.DoesNotExist:
                return None

            if product.promotion:
                # если на товар назначена скидка
                return product.promotion
            elif product.product.promotion_group:
                # если товар входит в скидочную группу
                return product.product.promotion_group.promotion
            else:
                return None

    def get_basket_promotion(self, products: QuerySet) -> float:
        """
        Получить скидку на корзину.

        :param products: Товары в корзине.
        :return: Общая скидка по всем товарам, которую нужно вычесть из общей суммы
            корзины, чтобы получить итоговую стоимость.
        """
        promotions = self.get_priority_promotions(products)
        products = ShopProduct.objects.filter(product__pk__in=list(promotions.keys()))
        products = {p.pk: float(p.price_in_shop) for p in products}

        discount: float = 0
        for pk, promos in promotions.items():
            for promo in promos:
                discount += products[pk] * promo.discount * 0.01

        return round(discount, 2)
