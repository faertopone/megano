from django.contrib.auth import user_logged_in
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver


class Client(models.Model):
    """Основная модель пользователя"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("пользователь")
    )
    postcode = models.IntegerField(_("почтовый индекс"), blank=True, null=True)
    photo = models.ImageField(_("фотография"), upload_to='accounts/', null=True, blank=True)
    phoneNumberRegex = RegexValidator(
        regex=r"^\+?7?\d{8,15}$",
        message='Введите корректный номер, без пробелов (+79999999999)'
    )
    phone = models.CharField(unique=True, null=True,
                             verbose_name=_('контактный номер'),
                             validators=[phoneNumberRegex],
                             max_length=16,
                             )
    city = models.CharField(_('город'), max_length=256, blank=True)
    street = models.CharField(_("улица"), max_length=256, blank=True)
    house_number = models.IntegerField(_("номер дома"), blank=True, null=True)
    apartment_number = models.IntegerField(
        _("номер квартиры"),
        blank=True, null=True
    )
    spent_money = models.DecimalField(
        _("потратил денег"),
        max_digits=9,
        decimal_places=2,
        default=0
    )
    is_seller = models.BooleanField(_("продавец"), default=False)

    patronymic = models.CharField(default='', max_length=50,
                                  error_messages={'max_length': 'Слишком длинное Отчество!'},
                                  verbose_name=_('Отчество'))

    item_view = models.ManyToManyField('products.Product', verbose_name=_('Товары, которые смотрел пользователь'),
                                       blank=True)
    limit_items_views = models.IntegerField(verbose_name=_('Сколько максимум показывать товаров'),
                                            help_text=_('Тут можно изменить это значение, по умолчанию 20 минимум 4.'),
                                            default=20, validators=[MinValueValidator(4)],
                                            blank=True,
                                            )
    item_in_page_views = models.IntegerField(verbose_name=_('По сколько товаров выводить на странице'),
                                             default=8,
                                             help_text=_('По сколько товаров будет добавляться при нажатии на кнопку '
                                                         '"показать еще", но не больше чем разрешено'),
                                             validators=[MinValueValidator(2)],
                                             error_messages={'min_length': 'Не стоит устанавливать меньше 2!'},
                                             blank=True,
                                             )

    # Проверяем, не больше ли чем позволено
    def item_in_page_views_check(self):
        if self.item_in_page_views >= self.limit_items_views:
            self.item_in_page_views = self.limit_items_views
        return self.item_in_page_views

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'
        db_table = 'Client'


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
