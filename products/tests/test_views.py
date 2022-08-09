from django.conf import settings
from django.db import models
from django.test import TestCase
from django.urls import reverse

from promotions.models import Promotions, PromotionGroup
from shops.models import Shops, ShopProduct
from ..models import Category, Product, Property, PropertyProduct, PropertyCategory
from ..views import (CategoryProductListView, PromotionProductListView, PromotionGroupProductListView,
                     SearchedProductListView)


settings.DEBUG = False
try:
    settings.MIDDLEWARE.remove("debug_toolbar.middleware.DebugToolbarMiddleware")
except ValueError:
    pass


class SetupTestDataMixin:
    @classmethod
    def setUpTestData(cls):
        # магазин
        shop = Shops.objects.create(
            name="Тестовый магазин",
            city="city", street="street",
            phone="123", email="test@test.com",
        )

        # категория товаров
        cls.category = Category.objects.create(
            category_name="Тестовые товары",
        )

        # скидки
        cls.promo10 = Promotions.objects.create(
            name="Минус 10%",
            discount=10,
        )
        cls.promo_group = PromotionGroup.objects.create(
            name="Группа тестовых товаров",
            promotion=cls.promo10,
        )

        # свойства товаров
        cls.prop1 = Property.objects.create(name="Свойство1", alias="prop1")
        cls.prop2 = Property.objects.create(name="Свойство2", alias="prop2")

        # привязываем свойства к категори товаров
        PropertyCategory.objects.create(category=cls.category, property=cls.prop1)
        PropertyCategory.objects.create(category=cls.category, property=cls.prop2)

        # товары
        cls.products_count = 6
        for i in range(1, cls.products_count + 1):
            product = Product.objects.create(
                name=f"Товар {i}",
                article=f"{i}",
                category=cls.category,
                price=i * 1000
            )
            shop.products.add(product)

            shop_product = ShopProduct.objects.get(product=product)
            shop_product.price_in_shop = i * 1000

            if i % 2 == 0:
                product.promotion_group = cls.promo_group
                # привязываем свойства к товарам
                PropertyProduct.objects.create(product=product, property=cls.prop1, value="Значение1")
            else:
                shop_product.promotion = cls.promo10
                # привязываем свойства к товарам
                PropertyProduct.objects.create(product=product, property=cls.prop2, value="Значение2")

            product.save()
            shop_product.save()


class TestViews(SetupTestDataMixin, TestCase):
    """
    Тестирование представлений.
    """

    def _test_response_with_products(self, response, template_name):
        self.assertEquals(response.status_code, 200)
        self.assertIn(template_name, response.template_name)
        self.assertIn("products", response.context_data)

    def test_products_in_category_page(self):
        """
        Проверка, что страница категории товаров существует и использует правильный шаблон.
        """
        response = self.client.get(reverse("products:product_list", kwargs={"pk": self.category.pk}))

        self._test_response_with_products(response, CategoryProductListView.template_name)
        self.assertEquals(response.context_data["products"].count(), self.products_count)

    def test_products_with_promotion_page(self):
        """
        Проверка, что страница со списком товаров, на которые назначена персональная
        скидка, существует и использует правильный шаблон.
        """
        response = self.client.get(reverse("products:product_sale", kwargs={"pk": self.promo10.pk}))

        self._test_response_with_products(response, PromotionProductListView.template_name)
        self.assertEquals(
            response.context_data["products"].count(),
            ShopProduct.objects.filter(~models.Q(promotion__isnull=True)).count()
        )

    def test_products_with_promotion_group_page(self):
        """
        Проверка, что страница со списком товаров, которые входят в
        группу скидок, существует и использует правильный шаблон.
        """
        response = self.client.get(reverse("products:product_sale_group", kwargs={"pk": self.promo_group.pk}))

        self._test_response_with_products(response, PromotionGroupProductListView.template_name)
        self.assertEquals(
            response.context_data["products"].count(),
            ShopProduct.objects.filter(~models.Q(product__promotion_group=True)).count()
        )

    def test_products_that_searched_page(self):
        """
        Проверка, что страница со списком найденных товаров, существует и использует правильный шаблон.
        """
        response = self.client.get(reverse("products:product_search"))

        self._test_response_with_products(response, SearchedProductListView.template_name)
        self.assertEquals(response.context_data["products"].count(), self.products_count)


class TestFilterProductsInCategory(SetupTestDataMixin, TestCase):
    """
    Тестирование фильтрации товаров в категории каталога.
    """

    def test_filter_one_by_name(self):
        """
        Проверка фильтрации одного товара по названию товара.
        """
        response = self.client.get(
            reverse("products:product_list", kwargs={"pk": self.category.pk}) + "?product_name=Товар 1"
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context_data["products"].count(), 1)

    def test_filter_many_by_name(self):
        """
        Проверка фильтрации нескольких товаров по названию товара.
        """
        response = self.client.get(
            reverse("products:product_list", kwargs={"pk": self.category.pk}) + "?product_name=Товар"
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context_data["products"].count(), self.products_count)

    def test_filter_one_by_price(self):
        """
        Проверка фильтрации одного товара по цене.
        """
        response = self.client.get(
            reverse("products:product_list", kwargs={"pk": self.category.pk}) +
            "?product_price_min=1000&product_price_max=1000"
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context_data["products"].count(), 1)

    def test_filter_many_by_price(self):
        """
        Проверка фильтрации нескольких товаров по цене.
        """
        response = self.client.get(
            reverse("products:product_list", kwargs={"pk": self.category.pk}) +
            "?product_price_min=1000"
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context_data["products"].count(), self.products_count)

    def test_filter_by_one_prop(self):
        """
        Проверка филтрации по свойству.
        """
        response = self.client.get(
            reverse("products:product_list", kwargs={"pk": self.category.pk}) +
            "?prop1=Значение1"
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response.context_data["products"].count(),
            ShopProduct.objects.filter(product__product_property__value="Значение1").count()
        )

    def test_filter_by_many_props(self):
        """
        Проверка филтрации по нескольким свойствам.
        """
        response = self.client.get(
            reverse("products:product_list", kwargs={"pk": self.category.pk}) +
            "?prop1=Значение1&product_name=Товар"
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(
            response.context_data["products"].count(),
            ShopProduct.objects.filter(product__product_property__value="Значение1").count()
        )


class TestSearchProducts(SetupTestDataMixin, TestCase):
    """
    Тестирование поиска товаров.
    """

    def test_search_products(self):
        """
        Проверка поиска товаров.
        """
        response = self.client.get(reverse("products:product_search") + "?search=Товар")

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context_data["products"].count(), self.products_count)
