from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, FileExtensionValidator
from django.forms import TextInput, FileInput
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _

from accounts.models import Client
from accounts.tasks import send_client_email_task


class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2',
        )

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Такой пользователь уже существует')
        return username

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError('Пароли не совпадают')
        return cd['password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Пользователь с такой почтой уже зарегистрирован'
            )
        return email


class PwdResetForm(PasswordResetForm):
    email = forms.EmailField(max_length=254)

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email).first()
        if not user or not user.is_active:
            raise forms.ValidationError(
                'Пользователя с таким email нет')
        return email

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """Переопределяем метод для отправки через celery"""
        send_client_email_task.delay(
            user_id=context['user'].id,
            site=context['domain'],
            subject='Восстановление пароля',
            template='password_reset'
        )


class ProfileEditForm(forms.ModelForm):
    """
    Форма для редактирования профиля
    """

    # Добавление класса в inputs
    wd1 = FileInput(attrs={'class': 'Profile-file', 'type': 'file'})
    wd2 = TextInput(attrs={'class': 'form-input'})
    wd3 = TextInput(attrs={'class': 'form-input', 'placeholder': _('Данных нет'), 'data-validate': 'require'})

    photo = forms.ImageField(required=False,
                             widget=wd1,
                             validators=[FileExtensionValidator(allowed_extensions=('gif', 'jpg', 'png'))],
                             error_messages={'invalid_image': 'Этот формат не поддерживается'})
    phone = forms.CharField(required=False,
                            widget=wd2,
                            validators=[RegexValidator(
                                regex=r"^\+?7?\d{8,15}$",
                                message='Введите корректный номер, без пробелов (+79999999999)')]
                            )
    patronymic = forms.CharField(required=True, widget=wd3)

    password1 = forms.CharField(required=False,
                                widget=forms.PasswordInput(
                                    attrs={'class': 'form-input', 'placeholder': _('Тут можно изменить пароль'), }))
    password2 = forms.CharField(required=False,
                                widget=forms.PasswordInput(
                                    attrs={'class': 'form-input', 'placeholder': _('Введите пароль повторно')}))
    id_user = forms.IntegerField(widget=forms.HiddenInput())

    limit_items_views = forms.IntegerField(widget=wd2)
    item_in_page_views = forms.IntegerField(widget=wd2)

    class Meta:
        model = User
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

    def clean_photo(self):
        # Ограничение размера файла не более 2Мбайт
        MAX_FILE_ZISE = 2097152
        photo = self.files.get('photo')
        if photo:
            if photo.size > MAX_FILE_ZISE:
                err_msg = 'Размер файла не должен превышать {}'.format(filesizeformat(MAX_FILE_ZISE))
                raise ValidationError(err_msg)
        return photo

    def clean_item_in_page_views(self):
        item_in_page_views = self.cleaned_data.get('item_in_page_views')
        if item_in_page_views <= 2:
            raise ValidationError('Не стоит устанавливать меньше 2!')
        return item_in_page_views

    def clean_limit_items_views(self):
        limit_items_views = self.cleaned_data.get('limit_items_views')
        if limit_items_views < 4:
            raise ValidationError('Ну уж меньше 4, это не серьезно!')
        return limit_items_views

    def clean(self):
        cleaned_data = super().clean()
        id_user = cleaned_data.get('id_user')
        user = User.objects.get(id=id_user)
        client = Client.objects.get(user=user)
        phone = cleaned_data.get('phone')
        email = cleaned_data.get('email')
        errors = {}
        if User.objects.filter(email=email).exists():
            email_in_bd = User.objects.filter(email=email).first()
            if user.email != email and email == email_in_bd.email:
                errors['email'] = ValidationError('Такой email уже занят')

        if Client.objects.filter(phone=phone).exists():
            client_in_bd = Client.objects.filter(phone=phone).first()
            if client.phone != phone and phone == client_in_bd.phone:
                errors['phone'] = ValidationError('Такой телефон уже занят')

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 != password2:
            errors['password2'] = ValidationError('Ошибка, повторите пароль внимательнее!')
        if errors:
            raise ValidationError(errors)
