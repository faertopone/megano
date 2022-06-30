from django.test import TestCase

from products.models import Product, Category
from promotions.models import Promotions, PromotionGroup
from shops.models import Shops, ShopProduct

from ..services import PromotionService


class TestPromoService(TestCase):
    """
    Тестирование сервиса скидок.
    """

    @classmethod
    def setUpTestData(cls):
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
        for i in range(1, 7):
            product = Product.objects.create(
                name=f"Товар {i}",
                article=f"{i}",
                category=category,
                price=i * 1000
            )
            shop.products.add(product)

            shop_product = ShopProduct.objects.get(product=product)
            shop_product.price_in_shop = i * 1000

            if i == 1:
                product.promotion_group = cls.promo_group
            elif i == 2:
                shop_product.promotion = cls.promo10
            elif i == 3:
                shop_product.promotion = cls.promo20
            elif i == 4:
                product.promotion_group = cls.promo_group
                shop_product.promotion = cls.promo30

            product.save()
            shop_product.save()

    def test_get_all_promotions_for_many(self):
        promos = self.promo_service.get_all_promotions(ShopProduct)

        self.assertIs(promos.__class__, dict)
        self.assertEqual(len([promo for promos_ in promos.values() for promo in promos_]), 5)

        self.assertEqual(promos, {
            ShopProduct.objects.get(product__name="Товар 1").pk: [self.promo_group.promotion],
            ShopProduct.objects.get(product__name="Товар 2").pk: [self.promo10],
            ShopProduct.objects.get(product__name="Товар 3").pk: [self.promo20],
            ShopProduct.objects.get(product__name="Товар 4").pk: [self.promo30, self.promo_group.promotion],
        })

    def test_get_all_promotions_for_one_with_promo(self):
        shop_product = ShopProduct.objects.get(product__name="Товар 2")
        promos = self.promo_service.get_all_promotions(ShopProduct, pk=shop_product.pk)

        self.assertIs(promos.__class__, dict)
        self.assertEqual(len(promos[shop_product.pk]), 1)

        self.assertEqual(promos, {
            shop_product.pk: [self.promo10],
        })

    def test_get_all_promotions_for_one_with_promo_group(self):
        shop_product = ShopProduct.objects.get(product__name="Товар 1")
        promos = self.promo_service.get_all_promotions(ShopProduct, pk=shop_product.pk)

        self.assertIs(promos.__class__, dict)
        self.assertEqual(len(promos[shop_product.pk]), 1)

        self.assertEqual(promos, {
            shop_product.pk: [self.promo_group.promotion],
        })

    def test_get_all_promotions_for_one_with_promo_and_promo_group(self):
        shop_product = ShopProduct.objects.get(product__name="Товар 4")
        promos = self.promo_service.get_all_promotions(ShopProduct, pk=shop_product.pk)

        self.assertIs(promos.__class__, dict)
        self.assertEqual(len(promos[shop_product.pk]), 2)

        self.assertEqual(promos, {
            shop_product.pk: [self.promo30, self.promo_group.promotion],
        })

    def test_get_priority_promotions_for_many(self):
        promos = self.promo_service.get_priority_promotions(ShopProduct)

        self.assertIs(promos.__class__, dict)
        self.assertEqual(len([promo for promos_ in promos.values() for promo in promos_]), 4)

        self.assertEqual(promos, {
            ShopProduct.objects.get(product__name="Товар 1").pk: [self.promo_group.promotion],
            ShopProduct.objects.get(product__name="Товар 2").pk: [self.promo10],
            ShopProduct.objects.get(product__name="Товар 3").pk: [self.promo20],
            ShopProduct.objects.get(product__name="Товар 4").pk: [self.promo30],
        })

    def test_get_priority_promotions_for_one_with_promo(self):
        shop_product = ShopProduct.objects.get(product__name="Товар 2")
        promo = self.promo_service.get_priority_promotions(ShopProduct, pk=shop_product.pk)

        self.assertIs(promo.__class__, Promotions)
        self.assertEqual(promo, self.promo10)

    def test_get_priority_promotions_for_one_with_promo_group(self):
        shop_product = ShopProduct.objects.get(product__name="Товар 1")
        promo = self.promo_service.get_priority_promotions(ShopProduct, pk=shop_product.pk)

        self.assertIs(promo.__class__, Promotions)
        self.assertEqual(promo, self.promo_group.promotion)

    def test_get_priority_promotions_for_one_with_promo_and_promo_group(self):
        shop_product = ShopProduct.objects.get(product__name="Товар 4")
        promo = self.promo_service.get_priority_promotions(ShopProduct, pk=shop_product.pk)

        self.assertIs(promo.__class__, Promotions)
        self.assertEqual(promo, self.promo30)

    def test_get_basket_promotion(self):
        basket = ShopProduct.objects.filter(product__name__in=["Товар 1", "Товар 2", "Товар 4", "Товар 5"])
        total_basket_price = float(sum(p.price_in_shop for p in basket))

        price_with_discount: float = total_basket_price
        for p in basket:
            if p.promotion:
                price_with_discount -= float(p.price_in_shop) * p.promotion.discount * 0.01
            elif p.product.promotion_group:
                price_with_discount -= float(p.price_in_shop) * p.product.promotion_group.promotion.discount * 0.01

        self.assertEqual(total_basket_price - self.promo_service.get_basket_promotion(basket), price_with_discount)
