from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, FileExtensionValidator, EmailValidator
from django.forms import TextInput, PasswordInput, FileInput, HiddenInput
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _
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
    wd1 = FileInput(attrs={'class': 'form-input', 'type': 'file'})
    wd2 = TextInput(attrs={'class': 'form-input'})

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
    family_name_lastname = forms.CharField(required=False, widget=wd2 )

    password1 = forms.CharField(required=False,
                                widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': _('Тут можно изменить пароль')}))
    password2 = forms.CharField(required=False,
                                widget=forms.PasswordInput(
                                    attrs={'class': 'form-input', 'placeholder': _('Введите пароль повторно')}))

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'photo', 'phone', 'family_name_lastname']
        widgets = {'email': TextInput(attrs={
            'class': 'form-input',
            'placeholder': _('Ваш email')
        }),
        }
    # Скрытое поля, для проверки email - текущего пользователя
    id_user = forms.IntegerField(widget=HiddenInput)

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
        id_user = cleaned_data.get('id_user')
        user = User.objects.get(id=id_user)
        email = cleaned_data.get('email')
        errors = {}
        print(user.email, email)
        if User.objects.filter(email=email).exists():
            email_in_bd = User.objects.filter(email=email).first()
            print(user.email, email, email_in_bd.email)
            if user.email != email and email == email_in_bd.email:
                errors['email'] = ValidationError('Такой email уже занят')

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 != password2:
            errors['password2'] = ValidationError('Ошибка, повторите пароль внимательнее!')
        if errors:
            raise ValidationError(errors)
