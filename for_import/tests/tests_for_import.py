from django.conf import settings
from django.urls import reverse
from django.test import TestCase
from django.core.cache import cache
from django.contrib.auth.models import User

from shops.models import Shops, ShopUser


settings.DEBUG = False
try:
    settings.MIDDLEWARE.remove("debug_toolbar.middleware.DebugToolbarMiddleware")
except ValueError:
    pass


class TestForImport(TestCase):
    """
    Тестирование доступности импорта файлов в базу
    в зависимости от ролей пользователей
    """

    @classmethod
    def setUpTestData(cls):

        cls.user = User.objects.create_user(username='NotShop', password='NotShop777')
        User.objects.create_user(username='UserShop', password='UserShop777')
        User.objects.create_superuser(username='SuperUser', password='SuperUser777')

        cls.shop = Shops.objects.create(name="Тестовый магазин",
                                        city="city", street="street",
                                        phone="123", email="test@test.com",)

        cls.user_shop = ShopUser.objects.create(shop=cls.shop, user=cls.user)
        cls.user_shop.save()
        cache.set('UserShop_shop', [cls.shop], 3600)

    def test_import_product_html(self):
        """
        Проверка захода на страницу импорта продавцу и простому пользователю
        """
        response = self.client.get(reverse('import-product'))
        self.assertRedirects(response, reverse('login'), 302)

        self.client.force_login(User.objects.get(username='UserShop'))
        response = self.client.get(reverse('import-product'))
        self.assertEqual(response.status_code, 200)

        self.client.force_login(User.objects.get(username='NotShop'))
        response = self.client.get(reverse('import-product'))
        self.assertEqual(response.status_code, 302)

    def test_super_user_profile(self):
        """
        Проверка, что супер-юзер может зайти на страницу импорта
        """
        self.client.force_login(User.objects.get(username='SuperUser'))
        response = self.client.get(reverse('import-product'))
        self.assertEqual(response.status_code, 200)

    def test_profile_data_in_page(self):
        """
        Проверка на наличие статуса продавца
        """
        self.client.force_login(User.objects.get(username='UserShop'))
        response = self.client.get(reverse('profile'))
        item = response.context_data.get('user_shop')
        self.assertEqual("yes", item)  # None

        self.client.force_login(User.objects.get(username='SuperUser'))
        response = self.client.get(reverse('profile'))
        item = response.context_data.get('user_shop')
        self.assertEqual("yes", item)

        self.client.force_login(User.objects.get(username='NotShop'))
        response = self.client.get(reverse('profile'))
        item = response.context_data.get('user_shop')
        self.assertNotEqual("yes", item)

    def test_text_in_contains_user_shop(self):
        """
        Проверка вывода ссылок продавцу
        """
        self.client.force_login(User.objects.get(username='UserShop'))
        response = self.client.get(reverse('profile'))
        self.assertContains(response, 'В раздел администрирования')
        self.assertContains(response, 'Импортировать данные')
        response = self.client.get(reverse('import-product'))
        self.assertNotContains(response, 'У Вас права администратора')

    def test_text_in_contains_user(self):
        """
        Проверка вывода ссылок пользователю (не являющимся продавцом)
        """
        self.client.force_login(User.objects.get(username='NotShop'))
        response = self.client.get(reverse('profile'))
        self.assertNotContains(response, 'В раздел администрирования')
        self.assertNotContains(response, 'Импортировать данные')

    def test_text_in_contains_super_user(self):
        """
        Проверка вывода ссылок супер-пользователю
        """
        self.client.force_login(User.objects.get(username='SuperUser'))
        response = self.client.get(reverse('profile'))
        self.assertContains(response, 'В раздел администрирования')
        self.assertContains(response, 'Импортировать данные')
        response = self.client.get(reverse('import-product'))
        self.assertContains(response, 'У Вас права администратора')
