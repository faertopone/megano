from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator


def banners_directory_path(instance, filename):
    # путь, куда будет осуществлена загрузка media/banners_photo/name_баннера + <filename>
    return 'banners_photo/{name}_photo_+{filename}'.format(name=instance.name, filename=filename)


class Banners(models.Model):
    """
    Модель баннеров, которые используются для рекламы на сайте
    """
    name = models.CharField(max_length=15, verbose_name=_('Заголовок баннера'), unique=True)
    product_banner = models.ForeignKey("products.Product", on_delete=models.CASCADE,
                                       verbose_name=_("товар"),
                                       help_text=_('выберите товар, которому соответствует баннер'), null=True,
                                       blank=True)

    photo = models.ImageField(upload_to=banners_directory_path, null=True,
                              validators=(FileExtensionValidator(["jpeg", "jpg", "png", "svg"]),),
                              verbose_name=_("иконка баннера"),
                              help_text=_('Загрузите фотографию не более 3Мб, допустимый формат: jpeg, jpg, png, svg'))
    description = models.TextField(blank=True, verbose_name=_('описание'),
                                   help_text=_('Опишите что это за баннер'))
    is_active = models.BooleanField(default=True, verbose_name=_('статус активности'))
    creation_date = models.DateTimeField(verbose_name='дата создания', auto_now_add=True)

    def get_name_not_digital(self):
        """
        Возвращает имя товара без цифр (версии/серии)
        """
        full_name = self.name
        name_list = full_name.split()
        digit = None
        if isinstance(name_list, list):
            for i_name in name_list:
                if i_name.isdigit():
                    digit = i_name
                    break
        if digit:
            name_list.remove(digit)
            full_name = ' '.join(name_list)
        return full_name

    def get_version(self):
        """
        Возвращает цифры, если в названии товара они есть, или возвращает None если нету
        """
        name = self.product_banner.name
        name_list = name.split()
        if isinstance(name_list, list):
            for i_name in name_list:
                if i_name.isdigit():
                    return i_name
        return None

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Banners'
        verbose_name = _('баннер')
        verbose_name_plural = _('баннеры')
