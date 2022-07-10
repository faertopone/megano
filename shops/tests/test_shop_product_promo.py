from django.conf import settings
from django.test import TestCase

from products.models import Product, Category
from promotions.models import Promotions, PromotionGroup
from promotions.services import PromotionService

from ..models import Shops, ShopProduct


class TestShopProductPromo(TestCase):
    """
    Тестирование интеграции с сервисом скидок.
    """

    @classmethod
    def setUpTestData(cls):
        settings.DEBUG_TOOLBAR_PANELS.remove("debug_toolbar.panels.sql.SQLPanel")

        cls.promo_service = PromotionService()

        # магазин
        shop = Shops.objects.create(
            name="Тестовый магазин",
            city="city", street="street",
            phone="123", email="test@test.com",
        )

        # категория товаров
        category = Category.objects.create(
            category_name="Тестовые товары",
        )

        # скидки
        cls.promo10 = Promotions.objects.create(
            name="Минус 10%",
            discount=10,
        )
        cls.promo20 = Promotions.objects.create(
            name="Минус 20%",
            discount=20,
        )
        cls.promo30 = Promotions.objects.create(
            name="Минус 30%",
            discount=30,
        )
        cls.promo_group = PromotionGroup.objects.create(
            name="Группа тестовых товаров",
            promotion=cls.promo10,
        )

        # товары
        for i in range(1, 5):
            product = Product.objects.create(
                name=f"Товар {i}",
                article=f"{i}",
                category=category,
                price=1000
            )
            shop.products.add(product)

            shop_product = ShopProduct.objects.get(product=product)
            shop_product.price_in_shop = 1000

            if i == 1:
                product.promotion_group = cls.promo_group
            elif i == 2:
                shop_product.promotion = cls.promo10
            elif i == 3:
                product.promotion_group = cls.promo_group
                shop_product.promotion = cls.promo30

            product.save()
            shop_product.save()

    def test_get_priority_promotion_if_promo(self):
        """
        Проверка получения приоритетной скидки, когда на товар назначена
        персональная скидка.
        """
        shop_product = ShopProduct.objects.get(product__name="Товар 2")

        priority_promo = shop_product.get_priority_promotion(self.promo_service)

        self.assertEquals(priority_promo, self.promo10)

    def test_get_priority_promotion_if_promo_group(self):
        """
        Проверка получения приоритетной скидки, когда на товар входит в группу
        товаров со скидкой.
        """
        shop_product = ShopProduct.objects.get(product__name="Товар 1")

        priority_promo = shop_product.get_priority_promotion(self.promo_service)

        self.assertEquals(priority_promo, self.promo_group.promotion)

    def test_get_priority_promotion_if_promo_and_promo_group(self):
        """
        Проверка получения приоритетной скидки, когда на товар назначена
        персональная скидка и он входит в группу товаров со скидкой.
        """
        shop_product = ShopProduct.objects.get(product__name="Товар 3")

        priority_promo = shop_product.get_priority_promotion(self.promo_service)

        self.assertEquals(priority_promo, self.promo30)

    def test_get_priority_promotion_if_no_promo(self):
        """
        Проверка получения приоритетной скидки, когда на товар не назначено
        никаких скидок.
        """
        shop_product = ShopProduct.objects.get(product__name="Товар 4")

        priority_promo = shop_product.get_priority_promotion(self.promo_service)

        self.assertIs(priority_promo, None)

    def test_get_priority_promotion_discount_if_promo(self):
        """
        Проверка получения величины приоритетной скидки, когда на товар назначена
        персональная скидка.
        """
        shop_product = ShopProduct.objects.get(product__name="Товар 2")

        priority_promo_discount = shop_product.get_promotion_discount(self.promo_service)

        self.assertEquals(priority_promo_discount, round(self.promo10.discount, 2))

    def test_get_priority_promotion_discount_if_promo_group(self):
        """
        Проверка получения величины приоритетной скидки, когда на товар входит в группу
        товаров со скидкой.
        """
        shop_product = ShopProduct.objects.get(product__name="Товар 1")

        priority_promo_discount = shop_product.get_promotion_discount(self.promo_service)

        self.assertEquals(priority_promo_discount, round(self.promo_group.promotion.discount, 2))

    def test_get_priority_promotion_discount_if_promo_and_promo_group(self):
        """
        Проверка получения величины приоритетной скидки, когда на товар назначена
        персональная скидка и он входит в группу товаров со скидкой.
        """
        shop_product = ShopProduct.objects.get(product__name="Товар 3")

        priority_promo_discount = shop_product.get_promotion_discount(self.promo_service)

        self.assertEquals(priority_promo_discount, round(self.promo30.discount, 2))

    def test_get_priority_promotion_discount_if_no_promo(self):
        """
        Проверка получения величины приоритетной скидки, когда на товар не назначено
        никаких скидок.
        """
        shop_product = ShopProduct.objects.get(product__name="Товар 4")

        priority_promo_discount = shop_product.get_promotion_discount(self.promo_service)

        self.assertIs(priority_promo_discount, None)

    def test_get_promotion_discount(self):
        """
        Проверка получения величины скидки.
        """
        shop_product = ShopProduct.objects.get(product__name="Товар 1")

        promo_discount = shop_product.get_promotion_discount(self.promo_service, promotion=self.promo30)

        self.assertEquals(promo_discount, round(self.promo30.discount, 2))

    def test_get_priority_prices_with_promotion_if_promo(self):
        """
        Проверка получения цен приоритетной скидки, когда на товар назначена
        персональная скидка.
        """
        shop_product = ShopProduct.objects.get(product__name="Товар 2")

        prices = shop_product.get_prices_with_promotion(self.promo_service)
        expected_prices = (
            round(float(shop_product.price_in_shop), 2),
            round(float(shop_product.price_in_shop) -
                  float(shop_product.price_in_shop) * self.promo10.discount * 0.01, 2)
        )

        self.assertEquals(prices, expected_prices)

    def test_get_priority_prices_with_promotion_if_promo_group(self):
        """
        Проверка получения цен приоритетной скидки, когда на товар входит в группу
        товаров со скидкой.
        """
        shop_product = ShopProduct.objects.get(product__name="Товар 1")

        prices = shop_product.get_prices_with_promotion(self.promo_service)
        expected_prices = (
            round(float(shop_product.price_in_shop), 2),
            round(float(shop_product.price_in_shop) -
                  float(shop_product.price_in_shop) * self.promo_group.promotion.discount * 0.01, 2)
        )

        self.assertEquals(prices, expected_prices)

    def test_get_priority_prices_with_promotion_if_promo_and_promo_group(self):
        """
        Проверка получения цен приоритетной скидки, когда на товар назначена
        персональная скидка и он входит в группу товаров со скидкой.
        """
        shop_product = ShopProduct.objects.get(product__name="Товар 3")

        prices = shop_product.get_prices_with_promotion(self.promo_service)
        expected_prices = (
            round(float(shop_product.price_in_shop), 2),
            round(float(shop_product.price_in_shop) -
                  float(shop_product.price_in_shop) * self.promo30.discount * 0.01, 2)
        )

        self.assertEquals(prices, expected_prices)

    def test_get_priority_prices_with_promotion_if_no_promo(self):
        """
        Проверка получения цен приоритетной скидки, когда на товар не назначено
        никаких скидок.
        """
        shop_product = ShopProduct.objects.get(product__name="Товар 4")

        prices = shop_product.get_prices_with_promotion(self.promo_service)
        expected_prices = (
            round(float(shop_product.price_in_shop), 2),
            None
        )

        self.assertEquals(prices, expected_prices)

    def test_get_prices_with_promotion(self):
        """
        Проверка получения цен скидки.
        """
        shop_product = ShopProduct.objects.get(product__name="Товар 1")

        prices = shop_product.get_prices_with_promotion(self.promo_service, promotion=self.promo30)
        expected_prices = (
            round(float(shop_product.price_in_shop), 2),
            round(float(shop_product.price_in_shop) -
                  float(shop_product.price_in_shop) * self.promo30.discount * 0.01, 2)
        )

        self.assertEquals(prices, expected_prices)
