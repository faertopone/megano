from django import forms
from django.forms import TextInput
from django.utils.translation import gettext_lazy as _
from orders.models import Order


class OrderForm(forms.ModelForm):
    """
    Форма заполнения ЗАКАЗА
    """

    # Добавление класса в inputs
    wd2 = TextInput(attrs={'class': 'form-input'})
    wd3 = TextInput(attrs={'class': 'form-input', 'placeholder': _('Данных нет'), 'data-validate': 'require'})

    patronymic = forms.CharField(required=True, widget=wd3)

    id_order = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Order
        fields = ['email', 'password1', 'password2', 'photo', 'phone', 'patronymic', 'first_name', 'last_name']
        widgets = {'email': TextInput(attrs={
            'class': 'form-input',
            'placeholder': _('Данных нет'),

        }),
            'first_name': TextInput(attrs={
                'class': 'form-input',
                'placeholder': _('Данных нет'),
                'required': True,
                'data-validate': 'require',
            }),
            'last_name': TextInput(attrs={
                'class': 'form-input',
                'placeholder': _('Данных нет'),
                'required': True,
                'data-validate': 'require',
            }),
        }