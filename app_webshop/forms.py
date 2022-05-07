import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import ModelForm, forms, ImageField
from django.template.defaultfilters import filesizeformat

from .models import Banners




class BannersForm(ModelForm):
    """
    Форма создания баннеров для рекламы
    """

    def clean_photo(self):
        # Ограничение размера файла не более 3Мбайт
        MAX_FILE_ZISE = 3145728
        photo = self.files.get('photo')
        if photo:
            if photo.size > MAX_FILE_ZISE:
                err_msg = 'Размер файла не должен превышать {}'.format(filesizeformat(MAX_FILE_ZISE))
                raise ValidationError(err_msg)
        return photo

    class Meta:
        model = Banners
        fields = '__all__'


