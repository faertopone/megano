from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Client(models.Model):
    """Основная модель пользователя"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("пользователь")
    )
    postcode = models.IntegerField(_("почтовый индекс"))
    photo = models.ImageField(_("фотография"), upload_to='accounts/', null=True)
    phoneNumberRegex = RegexValidator(
        regex=r"^\+?7?\d{8,15}$",
        message='Введите корректный номер, без пробелов (+79999999999)'
    )
    phone = models.CharField(
        'контактный номер',
        validators=[phoneNumberRegex],
        max_length=16,
    )
    city = models.CharField(_('город'), max_length=256)
    street = models.CharField(_("улица"), max_length=256)
    house_number = models.IntegerField(_("номер дома"))
    apartment_number = models.IntegerField(_("номер квартиры"))
    spent_money = models.DecimalField(
        _("потратил денег"),
        max_digits=9,
        decimal_places=2,
        default=0
    )
    is_seller = models.BooleanField(_("продавец"), default=False)

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'

    def __str__(self):
        return self.user.first_name
