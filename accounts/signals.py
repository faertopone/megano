from django.contrib.auth import user_logged_in
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import Client
from products.models import Product


@receiver(user_logged_in)
def clone_history_items_after_login(request, user, **kwargs):
    """
    После того как пользователь залогиниться, выполним слияние из сессии данных в модель
    """

    if not request.user.is_superuser:
        client = Client.objects.get(user=user)
        session_user_products_id = request.session.get('products_session')
        if session_user_products_id:
            limit = client.limit_items_views
            # тут N последних просмотренных товаров
            all_items_history = client.item_view.all()[:limit]
            # Процесс добавления из сессии в модель

            for i in session_user_products_id:
                i_product = Product.objects.get(pk=i)
                # Если этого товара нет в последних просмотренных, добавим в модель
                if not (i_product in all_items_history):
                    client.item_view.add(i_product)

            # удаление истории из кеша
            request.session['products_session'].clear()
