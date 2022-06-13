from django.contrib.auth import user_logged_in
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import Client


# После сохранения модели User, создаем ему сразу в БД модель Client
@receiver(post_save, sender=User)
def created_client(sender, instance, created, **kwargs):
    if created:
        Client.objects.create(user=instance)


# После сохранения модели Client, сохраняем User
@receiver(post_save, sender=Client)
def client_save_user_save(sender, instance, created, **kwargs):
    instance.user.save()


# После того как пользователь залогиниться, выполним слияние из сессии данных в модель
@receiver(user_logged_in)
def clone_history_items_after_login(sender, request, user, **kwargs):
    # Если это не админ входит
    if not request.user.is_superuser:
        client = Client.objects.get(user=user)
        session_user_products = request.session.get('products')
        if session_user_products:
            limit = client.limit_items_views
            # тут N последних просмотренных товаров
            all_items_history = client.item_view.all()[:limit]
            # Процесс добавления из сессии в модель
            for i in session_user_products:
                # Если этого товара нет в последних просмотренных, добавим в модель
                if not (i in all_items_history):
                    client.item_view.add(i)

            # удаление истории из кеша
            del request.session['products']
