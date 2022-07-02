import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.defaultfilters import filesizeformat
from django.urls import reverse
from accounts.models import Client

from products.models import Product, Category
import tempfile
import shutil
from django.test import TestCase, override_settings


# Создаем временную папку для хранения файлов во время тестов
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ProfileTest(TestCase):

    @classmethod
    def tearDownClass(cls):
        """
        Удаляем временную папку после тестов
        """
        shutil.rmtree(settings.MEDIA_ROOT)
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        """
        Начальная настройка для тестов
        """
        name_file = 'Баннер_1_photo_video.png'
        # Создали тестовую категорию товара
        category_test = Category.objects.create(category_name='category_name_TEST', icon_photo=name_file)

        # Создадим 10 продуктов
        product_list = []
        for _ in range(100):
            name_item = f'TEST_NAME_PRODUCT+{str(_)}'
            product_test = Product.objects.create(name=name_item, category=category_test)
            product_list.append(product_test)

        # Создадим User
        user_1 = User.objects.create_user(username='TEST', password='password_TEST', email='test@mail.ru')
        user_2 = User.objects.create_user(username='TEST2', password='password_TEST2', email='test2@mail.ru')
        # Создадим Super_User
        super_user_new = User.objects.create_superuser(username='SUPER_TEST',
                                                       password='password_SUPER_TEST',
                                                       email='SUPER_TEST@mail.ru')
        # Создадим клиента (доп параметры от User)
        client = Client.objects.get(user=user_1)
        client2 = Client.objects.get(user=user_2)
        client2.phone = +79999999
        client2.save()
        # Добавим просмотренные товары
        for i_view in product_list:
            client.item_view.add(i_view)
            client.save()

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
            'phone': +79999999,
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
            'phone': +79999999999,
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
