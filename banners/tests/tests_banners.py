from django.test import TestCase
from django.urls import reverse
from banners.models import Banners
from products.models import Product, Category

COUNT_BANNERS = 10


class BannersTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        name_file = 'Баннер_1_photo_video.png'
        # Создали тестовую категорию товара
        category_test = Category.objects.create(category_name='category_name_TEST', icon_photo=name_file)
        # Создали тестовый товар
        product_test = Product.objects.create(name='TEST_NAME_PRODUCT', category=category_test)
        # Создали 10 баннеров
        for i_banner in range(COUNT_BANNERS):
            Banners.objects.create(
                name='test_' + str(i_banner),
                photo=name_file,
                product_banner=product_test,
                is_active=True
            )

    def test_banners_index(self):
        response = self.client.get(reverse('index'))
        content = response.context_data.get('banners')
        # Проверка, что выводится именно 3 баннера на странице, хотя изначально их 10
        self.assertEqual(3, len(content))
        self.assertEqual(response.status_code, 200)
