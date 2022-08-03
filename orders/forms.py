from django import forms
from django.forms import TextInput, EmailInput, RadioSelect
from django.utils.translation import gettext_lazy as _
from orders.models import Order


class OrderPay(forms.Form):

    number_visa = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input Payment-bill',
        'placeholder': '9999 9999',
        'data-mask': '9999 9999',
        'data-validate': 'require pay'
    }))

    def clean_number_visa(self):
        number_visa = self.cleaned_data.get('number_visa')
        str_visa = ''.join(number_visa.split())
        if str_visa.isdigit():
            return int(str_visa)
        raise forms.ValidationError('Введите только цифры')


class OrderForm(forms.ModelForm):
    """
    Форма заполнения ЗАКАЗА
    """

    class Meta:
        model = Order
        fields = ['email', 'payment', 'address', 'city', 'delivery', 'patronymic', 'first_name', 'last_name', 'phone']
        widgets = {'email': EmailInput(attrs={
            'class': 'form-input',
            'placeholder': _('Ваш email'),
            'data-validate': 'require',
        }),
            'first_name': TextInput(attrs={
                'class': 'form-input',
                'placeholder': _('Ваше Имя'),
                'data-validate': 'require',
            }),
            'last_name': TextInput(attrs={
                'class': 'form-input',
                'placeholder': _('Ваша Фамилия'),
                'data-validate': 'require',
            }),
            'city': TextInput(attrs={
                'class': 'form-input',
                'placeholder': _('Ваш город'),
                'data-validate': 'require',
            }),
            'patronymic': TextInput(attrs={
                'class': 'form-input',
                'placeholder': _('Ваше Отчество'),
                'data-validate': 'require',
            }),
            'phone': TextInput(attrs={
                'class': 'form-input',
                'placeholder': _('Ваш телефон'),
                'data-validate': 'require',
            }),
            'address': TextInput(attrs={
                'class': 'form-textarea',
                'type': 'textarea',
                'placeholder': _('Ваш Адрес'),
                'data-validate': 'require',
            }),
            'delivery': RadioSelect(),
            'payment': RadioSelect(),
        }
