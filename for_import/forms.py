from django import forms
from django.utils.translation import gettext_lazy as _
from .models import FixtureFile


class UploadFileForm(forms.Form):
    """
    File upload form
    """
    file = forms.FileField(label=_('file'))


class FileFieldForm(forms.Form):
    # class Meta:
    #     model = FixtureFile
    #     fields = '__all__'
    #     file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))