from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """
    Категория каталога товаров.
    """
    activity = models.BooleanField(
        default=True,
        verbose_name=_("Активность"),
        help_text=_("Если категория активна, то она должна отображаться в главном меню сайта")
    )
    icon_photo = models.FileField(upload_to="categories/", max_length=500,
                                  validators=(FileExtensionValidator(["jpeg", "jpg", "png", "svg"]),),
                                  verbose_name=_("Иконка категории"))
    category_name = models.CharField(max_length=1000, verbose_name=_("Название категории"))
    description = models.TextField(blank=True, verbose_name=_("Описание"),
                                   help_text=_("Опишите, например, какие товары соответствуют данной категории"))

    class Meta:
        verbose_name = _("категория каталога товаров")
        verbose_name_plural = _("категории каталога товаров")

    def __str__(self):
        return self.category_name
