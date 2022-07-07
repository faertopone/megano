from django import forms
from django.utils.translation import gettext_lazy as _


class UploadFileForm(forms.Form):
    """
    File upload form
    """
    file = forms.FileField(label=_('file'))