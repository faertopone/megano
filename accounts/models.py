from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Client(models.Model):
    """Основная модель пользователя"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь")
    )
    postcode = models.IntegerField(_("Почтовый индекс"))
    photo = models.ImageField(_("Фотография"), upload_to='accounts/', null=True)
    phoneNumberRegex = RegexValidator(
        regex=r"^\+?7?\d{8,15}$",
        message='Введите корректный номер, без пробелов (+79999999999)'
    )
    phone = models.CharField(
        'Контактный номер',
        validators=[phoneNumberRegex],
        max_length=16,
    )
    city = models.CharField(_('Город'), max_length=256)
    street = models.CharField(_("Улица"), max_length=256)
    house_number = models.IntegerField(_("Номер дома"))
    apartment_number = models.IntegerField(_("Номер квартиры"))
    spent_money = models.DecimalField(
        _("Потратил денег"),
        max_digits=9,
        decimal_places=2,
        default=0
    )
    is_seller = models.BooleanField(_("Продавец"), default=False)

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'

    def __str__(self):
        return self.user.first_name
