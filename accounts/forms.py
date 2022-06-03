from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, FileExtensionValidator, EmailValidator
from django.forms import HiddenInput
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import NON_FIELD_ERRORS
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

    def clean_user_name(self):
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


class ProfileEditForm(forms.Form):
    """
    Форма для редактирования профиля
    """

    photo = forms.ImageField(required=False, label=False,
                             widget=forms.FileInput(attrs={'class': 'form-input', 'type': 'file'}),
                             validators=[FileExtensionValidator(allowed_extensions=('gif', 'jpg', 'png'))],
                             error_messages={'invalid_extension': 'Этот формат не поддерживается'})
    phone = forms.CharField(label=False, required=False,
                            widget=forms.TextInput(attrs={'class': 'form-input'}),
                            validators=[RegexValidator(
                                regex=r"^\+?7?\d{8,15}$",
                                message='Введите корректный номер, без пробелов (+79999999999)')]
                            )
    email = forms.EmailField(label=False, required=False,
                             widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Ваш email')}))
    FIO = forms.CharField(label=False, required=False, max_length=100,
                          widget=forms.TextInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label=False, required=False,
                                widget=forms.PasswordInput(attrs={
                                        'class': 'form-input', 'placeholder': _('Тут можно изменить пароль')})
                                )
    password2 = forms.CharField(label=False, required=False,
                                widget=forms.PasswordInput(attrs={
                                        'class': 'form-input', 'placeholder': _('Введите пароль повторно')
                                    })
                                )

    id_client = forms.IntegerField(widget=HiddenInput)

    def clean_photo(self):
        # Ограничение размера файла не более 2Мбайт
        MAX_FILE_ZISE = 2097152
        photo = self.files.get('photo')
        if photo:
            if photo.size > MAX_FILE_ZISE:
                err_msg = 'Размер файла не должен превышать {}'.format(filesizeformat(MAX_FILE_ZISE))
                raise ValidationError(err_msg)
        return photo

    def clean(self):
        cleaned_data = super().clean()
        client_id = cleaned_data.get('id_client')
        user = User.objects.get(id=client_id)
        email = cleaned_data.get('email')
        errors = {}
        if User.objects.filter(email=email).exists():
            email_in_bd = User.objects.filter(email=email).first()
            if user.email != email:
                if email == email_in_bd.email:

                    errors['email'] = ValidationError('Такой email уже занят')

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 != password2:
            errors['password2'] = ValidationError('Ошибка, повторите пароль внимательнее!')

        if errors:

            raise ValidationError(errors)


