# Командный дипломный проект курса "Python-фреймворк Django"
Проект представляет собой интернет-магазин, где продавцы могут продавать свои товары, размещая на сайте информацию о себе и своих товарах.

В рамках проекта был реализован следующий функционал:
* Добавление/редактирование информации о продавце
* Каталог товаров, который разделяется на различные категории (например, одежда, электроника)
* Фильтрация в каталоге товаров
* Возможность назначать персональную скидку на конкретный товар
* Возможность назначать скидку на группу товаров
* Корзина товаров
* Оформление заказа
* Авторизация/регистрация пользователей
* Личный кабинет пользователя с историей заказов
* История просмотренных товаров, доступная в личном кабинете
* Возможность добавлять товары к сравнению
* Административный раздел, реализованный через админку Django.
* Импорт товаров
* Сайт доступен на двух языках: русский (``ru``) и английский (``en``)

## Технологический стэк
* Python 3
* Django 4
* Celery
* Redis
* Jinja2
* Vagrant (для локальной разработки)
* Postgres

## Установка для разработки
1. Клонировать репозиторий
   ```
   git clone https://github.com/faertopone/megano.git
   cd python_django_team9
   ```
2. Переключиться на ветку ``develop``
   ```
   git checkout -b develop origin/develop
   ```
3. Создать и активировать виртуальное окружение
4. Установить зависимости
   ```
   python -m pip install -r requirements\dev.txt
   ```
5. Установить redis-server
   ```
   sudo apt install redis-server
   ```
   Проверить что статус сервера active (running)
   ```
   systemctl status redis-server
   ```
6. Запустить celery worker
   ```
   celery -A config worker -l info
   ```
7. Запустить celery beat
   ```
   celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
   ```

## Выполнение задач по разработке
1. Перед выполнением очередной задачи нужно переключиться на ветку ``develop``
   ```
   git switch develop
   git pull
   ```
2. Затем создаем новую ветку для выполняемой задачи
   ```
   git checkout -b <branch_name>
   ```
   Одна задача - одна ветка. Имена веток должны иметь префиксы:
   * ``feature/`` - для ветки, в которой разрабатывается новый функционал. Например, ``feature/add_product_model``
3. Выполняется задача
4. :warning: Не забываем выполнить
   ```
   python -m flake8
   ```
   и исправить все, что не по PEP в нашем коде.
   Также можно добавить комментарий ``# noqa: <rule>``. ``<rule>`` будет видно в консоли, после запуска ``flake8``, если он найдет ошибки.
5. Пушим ветку в удаленный репозиторий
   ```
   git push -u origin <branch_name>
   ```
6. Идем на gitlab и создаем Merge Request.
   
   :warning: Не забываем, что мерджить надо в ветку ``develop``, потому что от нее мы создаем ветки.

## Экспорт фикстур
Если в ходе выполнения задачи были созданы модели, наполненные тестовыми данными, то их желательно выгрузить в виде фикстур, чтобы у коллег появилась возможность воспользоваться этими данными.

Все фиксутры выгружаются в папку ``fixtures`` в корне проекта. Фикстуры отдельных приложений должны храниться в папке с именем приложения, а сами файлы фикстур должны иметь имена соответствующих моделей в нижнем регистре. Если имя модели состоит из нескольких слов, то в имени файла они разделяются нижним подчеркиванием ``_``.

Например, фикстуры моделей ``Example`` и ``NewExample`` приложения ``example_app`` должны находиться по пути ``fixtures\example_app\example.json`` и ``fixtures\example_app\new_example.json``

Фикстуры экспортируем командой
```
python -Xutf8 manage.py dumpdata <app>.<model> --indent 2 -o fixtures\<app>\<lower_model_in_snake_case>.json
```

## Загрузка фикстур при разработке
Если в ветке ``develop`` появились новые фикстуры, то перед выполнением очередной задачи может потребоваться их загрузить в локальную БД.

1. Установить базу данных PostgreSQL
   (Если PostgreSQL установлен, шаг пропускается. 
    Ниже приведены команды для ОП Linux)
   ```
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   ```

   1.2. Создать новую базу данных
   ```
   sudo -u postgres createdb meganodb 
   ```

   1.3 Выполнить миграции
      ```
      python manage.py makemigrations
      python manage.py migrate
      ```
2. Загрузить фикстуры.

   :warning: Порядок загружки фикстур имеет значение, потому что таблицы имеют связи.

   :ok_hand: Необязательно загружать все фикстуры. Можно загрузить только те, которых не хватает. Главное чтобы они загружались в правильном порядке.   
   
   1. Загрузить суперпользователя
   ```
   python manage.py loaddata fixtures\superuser.json
   ```
   2. Загрузить скидки
   ```
   python manage.py loaddata fixtures\promotions\promotions.json fixtures\promotions\promotion_group.json
   ```
   3. Загрузить категории каталога и товары
   ```
   python manage.py loaddata fixtures\products\category.json fixtures\products\product.json fixtures\products\product_photo.json
   ```
   4. Загрузить свойства товаров и их связи с товарами и категориями
   ```
   python manage.py loaddata fixtures\products\property.json fixtures\products\property_product.json fixtures\products\property_category.json
   ```
   5. Загрузить баннеры
   ```
   python manage.py loaddata fixtures\banners\banners.json
   ```
   6. Загрузить 1 профиль (покупатель)  
   ```
   python manage.py loaddata fixtures\accounts\client.json
   ```
   7. Загрузить магазины
   ```
   python manage.py loaddata fixtures\shops\shop.json fixtures\shops\shop_photo.json fixtures\shops\shop_product.json
   ```
   8. Загрузить периодическую задачу
   ```
   python manage.py loaddata fixtures\basket\interval.json fixtures\basket\clearing_basket_every_60_min.json
   ```
   9. Загрузить модель "Товар дня"
   ```
   python manage.py loaddata fixtures/promotions/promo_product.json
   ```
   
   :warning: Не забываем добавлять здесь, как загружать новые фикстуры!
=
3. *
