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

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'
        db_table = 'Client'

    def __str__(self):
        return self.user.username

    # Переопределил метод save, чтобы методом save объекта Client-сразу сохранять и изменения в поле user через OneToOne
    def save(self, *args, **kwargs):
        self.user.save(*args, **kwargs)
        super(Client, self).save(*args, **kwargs)


class HistoryView(models.Model):
    """ Модель истории просмотров пользователя """

    client = models.OneToOneField(
        Client,
        on_delete=models.CASCADE,
        verbose_name=_("пользователь_чья история")
    )

    item_view = models.ManyToManyField('products.Product', verbose_name=_('Товары, которые смотрел пользователь'),
                                       blank=True, null=True)
    limit_items_views = models.IntegerField(verbose_name=_('Сколько максимум показывать товаров'),
                                            help_text=_('Тут можно изменить это значение, по умолчанию 20 минимум 4.'),
                                            default=20, validators=[MinValueValidator(4)])
    item_in_page_views = models.IntegerField(verbose_name=_('По сколько товаров выводить на странице'),
                                             default=8,
                                             help_text=_('По сколько товаров будет добавляться при нажатии на кнопку '
                                                         '"показать еще", но не больше чем разрешено'),
                                             validators=[MinValueValidator(2)])

    # Проверяем, не больше ли чем позволено
    def item_in_page_views_check(self):
        if self.item_in_page_views >= self.limit_items_views:
            self.item_in_page_views = self.limit_items_views
        return self.item_in_page_views


    def __str__(self):
        return f'История просмотров для {self.client.user.username}'

    # После сохранения модели Client, создаем ему сразу в БД модель просмотров
    @receiver(post_save, sender=Client)
    def created_history(sender, instance, created, **kwargs):
        if created:
            HistoryView.objects.create(client=instance)

            # Способ №2
        # instance = kwargs['instance']
        # # Если у пользователя нет модели просмотров, то создадим ее
        # if not HistoryReview.objects.filter(client=instance).exists():
        #     HistoryReview.objects.create(client=instance)

    class Meta:
        verbose_name = 'История просмотра'
        verbose_name_plural = 'Истории просмотров'
        db_table = 'HistoryReview'
        ordering = ("id",)
