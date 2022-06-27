from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.forms import ProfileEditForm
from accounts.models import Client
from products.models import Product, Category


class ProfileTest(TestCase):

    @classmethod
    def setUpTestData(cls):
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
        response = self.client.get(reverse('profile'))
        # Если хотим попасть в профиль не авторизованным, то попадаем на страницу 'login'
        self.assertRedirects(response, reverse('login'), 302)
        # А теперь авторизуемся
        self.client.login(username='TEST', password='password_TEST')
        # И зайдем в профиль
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_super_user_profile(self):
        self.client.login(username='SUPER_TEST', password='password_SUPER_TEST')
        response = self.client.get(reverse('profile'))
        # зайти супер юзеру в профиль
        self.assertEqual(response.status_code, 200)

    def test_profile_data_in_page(self):
        self.client.login(username='TEST', password='password_TEST')
        # И зайдем в профиль
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        # Проверим, что выводится 3 последних просмотренных товара
        list_view_item = response.context_data.get('list_item_views')
        self.assertEqual(3, len(list_view_item))

    def test_history_view_item(self):
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
        # За логинимся
        login = self.client.login(username='TEST', password='password_TEST')
        # найдем профиль этого юзера
        my_client = Client.objects.get(user=login)
        # "debug_toolbar.panels.templates.TemplatesPanel" - нужно убрать что бы работало -)
        response = self.client.get(reverse('profile-edit', kwargs={'pk': my_client.pk}))
        # Отлично, страница загрузилась!
        self.assertEqual(response.status_code, 200)
        # Пошлем post с информацией
        from_data = {'first_name': 'ettst',
                     'id_user': my_client.user_id,
                     'limit_items_views': 2,
                     'item_in_page_views': 1,
                     'email': 'test2@mail.ru',
                     'phone': +79999999,
                     }
        resp = self.client.post(reverse('profile-edit', kwargs={'pk': my_client.pk}), data=from_data, follow=True)
        self.assertEqual(resp.context_data['form'].is_valid(), False)
        self.assertEqual(resp.context_data.get('form').errors['item_in_page_views'], ['Не стоит устанавливать меньше 2!'])
        # Проверка, что такая почта уже занята
        self.assertEqual(resp.context_data.get('form').errors['email'],
                         ['Такой email уже занят'])
        self.assertEqual(resp.context_data.get('form').errors['patronymic'],
                         ['Обязательное поле.'])
        self.assertEqual(resp.context_data.get('form').errors['limit_items_views'],
                         ['Ну уж меньше 4, это не серьезно!'])
        self.assertEqual(resp.context_data.get('form').errors['phone'],
                         ['Такой телефон уже занят'])



