from django import forms
from django.utils.translation import gettext_lazy as _


class UploadFileForm(forms.Form):
    """
    Загрузка файла
    """
    file = forms.FileField(label=_('file'))


class FileFieldForm(forms.Form):
    """
    Загрузка нескольких файлов
    """
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
