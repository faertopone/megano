import os
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.defaultfilters import filesizeformat
from django.urls import reverse
from accounts.models import Client

from products.models import Product, Category, Property, PropertyCategory
from shops.models import Shops, ShopUser, ShopProduct
import tempfile
import shutil
from django.test import TestCase, override_settings


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ProfileTest(TestCase):

    @classmethod
    def tearDownClass(cls):
        """
        Удаляет временную папку после тестов
        """
        shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        """
        TestShop1, TestShop2 - магазины. User2 зарегистрированный пользователь.
        User1 является владельцем TestShop2 (shop1_user1_test).
        Хозяин TestShop2 не определён (доступен только суперюзеру super_user).
        У категории category_test_1 свойства с нечетным индексом в названии (property1, property3...)
        У категории category_test_2 свойства с четным индексом в названии (property2, property4...)
        Товары с нечётным индексом в названии относятся к нечетной категории и есть в первом магазине
        пример: TestShop1 -> product1(category_name_1), product3(category_name_1)...
                TestShop2 -> product2(category_name_2), product4(category_name_2)...
        """
        settings.DEBUG_TOOLBAR_PANELS.remove("debug_toolbar.panels.sql.SQLPanel")
        settings.DEBUG_TOOLBAR_PANELS.remove("debug_toolbar.panels.templates.TemplatesPanel")

        name_file = 'Баннер_1_photo_video.png'
        category_test_1 = Category.objects.create(category_name='category_name_1', icon_photo=name_file)
        category_test_2 = Category.objects.create(category_name='category_name_2', icon_photo=name_file)
        for i in range(1, 7, 2):
            property_1 = Property.objects.create(name="property" + str(i), tooltip="", alias="alias" + str(i))
            PropertyCategory.objects.create(property=property_1, category=category_test_1)

        for i in range(2, 8, 2):
            property_2 = Property.objects.create(name="property" + str(i), tooltip="", alias="alias" + str(i))
            PropertyCategory.objects.create(property=property_2, category=category_test_2)

        shop_test_1 = Shops.objects.create(name="TestShop1", description="test text",
                                           city="Moscow", street="Test street",
                                           house_number=1, phone="88007572345",
                                           email="test_shop@test.ru", rating=3)
        shop_test_2 = Shops.objects.create(name="TestShop2", description="test text",
                                           city="Rostov", street="Test street",
                                           house_number=1, phone="88005572345",
                                           email="test_shop2@test.ru", rating=3)

        product_list = []
        for i in range(100):
            name_item = f'product+{str(i)}'
            if i % 2 == 0:
                product_test = Product.objects.create(name=name_item, category=category_test_2)
                ShopProduct.objects.create(shop=shop_test_2, product=product_test,
                                           amount=10 + i, price_in_shop=10 * i)
            else:
                product_test = Product.objects.create(name=name_item, category=category_test_1)
                ShopProduct.objects.create(shop=shop_test_1, product=product_test,
                                           amount=10 + i, price_in_shop=10 * i)
            product_list.append(product_test)

        user_1 = User.objects.create_user(username='TEST', password='password_TEST', email='test@mail.ru')
        user_2 = User.objects.create_user(username='TEST2', password='password_TEST2', email='test2@mail.ru')
        super_user = User.objects.create_superuser(username='SUPER_TEST',
                                                   password='password_SUPER_TEST',
                                                   email='SUPER_TEST@mail.ru')
        client_1 = Client.objects.create(user=user_1)
        client_2 = Client.objects.create(user=user_2, phone=79999999)
        shop1_user1_test = ShopUser.objects.create(user=user_1, shop=shop_test_1)

    def test_profile_html(self):
        """
        Проверка захода на страницу профиля без авторизации и с авторизацией
        """
        response = self.client.get(reverse('profile'))
        # Если хотим попасть в профиль не авторизованным, то попадаем на страницу 'login'
        self.assertRedirects(response, reverse('login'), 302)
        # А теперь авторизуемся
        self.client.login(username='TEST', password='password_TEST')
        # И зайдем в профиль
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_super_user_profile(self):
        """
        Проверка, что супер-юзер может зайти в профиль
        """
        self.client.login(username='SUPER_TEST', password='password_SUPER_TEST')
        response = self.client.get(reverse('profile'))
        # зайти супер юзеру в профиль
        self.assertEqual(response.status_code, 200)

    def test_profile_data_in_page(self):
        """
        Проверка что выводит 3 последних просмотренных товара
        """
        self.client.login(username='TEST', password='password_TEST')
        # И зайдем в профиль
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        # Проверим, что выводится 3 последних просмотренных товара
        list_view_item = response.context_data.get('list_item_views')
        self.assertEqual(3, len(list_view_item))

    def test_history_view_item(self):
        """
        Проверка вывода истории просмотров на странице "история просмотров"
        """
        # За логинимся
        login = self.client.login(username='TEST', password='password_TEST')
        # найдем профиль этого юзера
        my_client = Client.objects.get(user=login)
        response = self.client.get(reverse('history_user', kwargs={'pk': my_client.pk}))
        # Отлично, страница загрузилась!
        self.assertEqual(response.status_code, 200)
        # Проверка показа нужного количество товаров
        self.assertEqual(my_client.item_in_page_views, len(response.context_data.get('list_item_views')))

    def test_profile_edit_form_no_valid(self):
        """
        Проверка полей формы на не валидность, во время редактирования.
        Выявление записей при не корректной формы
        """
        # За логинимся
        login = self.client.login(username='TEST', password='password_TEST')
        # найдем профиль этого юзера
        my_client = Client.objects.get(user=login)
        # "debug_toolbar.panels.templates.TemplatesPanel" - нужно убрать что бы работало -)
        response = self.client.get(reverse('profile-edit', kwargs={'pk': my_client.pk}))
        # Отлично, страница загрузилась!
        self.assertEqual(response.status_code, 200)
        # загрузим картинку
        test_img = SimpleUploadedFile("big_img.gif",
                                      open(os.path.join(os.path.dirname(__file__), "big_img.gif"), mode="rb").read(),
                                      content_type="image/*")
        # Пошлем post с информацией
        from_data = {
            'id_user': my_client.user.id,
            'limit_items_views': 2,
            'item_in_page_views': 1,
            'email': 'test2@mail.ru',
            'phone': 79999999,
            'photo': test_img,
            'password1': 'password_TEST1',
            'password2': 'password_TEST_NEW'
        }
        resp = self.client.post(reverse('profile-edit', kwargs={'pk': my_client.pk}), data=from_data, follow=True)
        self.assertEqual(resp.context_data['form'].is_valid(), False)
        self.assertEqual(resp.context_data.get('form').errors['password2'],
                         ['Ошибка, повторите пароль внимательнее!'])
        self.assertEqual(resp.context_data.get('form').errors['item_in_page_views'],
                         ['Не стоит устанавливать меньше 2!'])
        # Проверка, что такая почта уже занята
        self.assertEqual(resp.context_data.get('form').errors['email'],
                         ['Такой email уже занят'])
        self.assertEqual(resp.context_data.get('form').errors['patronymic'],
                         ['Обязательное поле.'])
        self.assertEqual(resp.context_data.get('form').errors['limit_items_views'],
                         ['Ну уж меньше 4, это не серьезно!'])
        self.assertEqual(resp.context_data.get('form').errors['phone'],
                         ['Такой телефон уже занят'])
        MAX_FILE_ZISE = 2097152
        self.assertEqual(resp.context_data.get('form').errors['photo'],
                         [f'Размер файла не должен превышать {filesizeformat(MAX_FILE_ZISE)}'])

    def test_profile_edit_form_valid(self):
        """
        Проверка полей формы на валидность, во время редактирования
        Проверка новых данных после изменения
        """
        # За логинимся
        login = self.client.login(username='TEST', password='password_TEST')
        # найдем профиль этого юзера
        my_client = Client.objects.get(user=login)
        # "debug_toolbar.panels.templates.TemplatesPanel" - нужно убрать что бы работало -)
        response = self.client.get(reverse('profile-edit', kwargs={'pk': my_client.pk}))
        # Отлично, страница загрузилась!
        self.assertEqual(response.status_code, 200)
        # загрузим картинку
        test_img = SimpleUploadedFile("good_img.jpg",
                                      open(os.path.join(os.path.dirname(__file__), "good_img.jpg"), mode="rb").read(),
                                      content_type="image/*")
        # Пошлем post с информацией
        from_data = {
            'id_user': my_client.user.id,
            'limit_items_views': 20,
            'item_in_page_views': 10,
            'email': 'test3@mail.ru',
            'phone': 79999999999,
            'photo': test_img,
            'first_name': 'TEST_FIRST_NAME',
            'last_name': 'TEST_LAST_NAME',
            'patronymic': 'TEST_otchestvo',
            'password1': 'password_TEST_NEW',
            'password2': 'password_TEST_NEW'
        }
        resp = self.client.post(reverse('profile-edit', kwargs={'pk': my_client.pk}), data=from_data)
        self.assertEqual(resp.status_code, 302)
        # Обновим тестовую БД новыми данными
        my_client.refresh_from_db()

        # Проверим что данные поменялись
        self.assertEqual(my_client.user.first_name, 'TEST_FIRST_NAME')
        self.assertEqual(my_client.limit_items_views, 20)
        self.assertEqual(my_client.item_in_page_views, 10)
        self.assertEqual(my_client.user.email, 'test3@mail.ru')
        self.assertEqual(my_client.phone, '79999999999')
        self.assertEqual(my_client.photo, 'accounts/good_img.jpg')
        self.assertEqual(my_client.patronymic, 'TEST_otchestvo')
        self.assertEqual(my_client.user.check_password('password_TEST_NEW'), True)
