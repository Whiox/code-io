"""Формы аутентификации."""

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from authentication.models import User


class RegisterForm(forms.Form):
    """Форма для регистрации нового пользователя.

    :ivar forms.CharField username: Имя пользователя
    :ivar forms.EmailField email: Электронная почта пользователя
    :ivar forms.CharField password: Пароль
    :ivar forms.CharField repeat_password: Повтор пароля
    """
    username = forms.CharField(
        label='',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Введите имя пользователя'
        })
    )
    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Электронная почта'
        })
    )
    password = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Введите пароль',
            'autocomplete': 'new-password'
        }),
        help_text="Пароль должен соответствовать требованиям безопасности."
    )
    repeat_password = forms.CharField(
        label='',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Повторите пароль',
            'autocomplete': 'new-password'
        })
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким именем уже существует.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с такой почтой уже зарегистрирован.")
        return email

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        try:
            validate_password(pwd)
        except ValidationError as exc:
            raise ValidationError(exc.messages)
        return pwd

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        pwd2 = cleaned_data.get('repeat_password')
        if pwd and pwd2 and pwd != pwd2:
            self.add_error('repeat_password', "Пароли не совпадают.")
        return cleaned_data


class LoginForm(forms.Form):
    """Форма для входа в аккаунт.

    :ivar forms.EmailField email: Электронная почта
    :ivar forms.CharField password: Пароль
    """
    email = forms.EmailField(
        label='', max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Электронная почта'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Введите пароль',
            'autocomplete': 'new-password'
        })
    )


class ResetPasswordForm(forms.Form):
    """Форма запроса на сброс пароля.

    :ivar forms.EmailField email: Электронная почта
    """
    email = forms.EmailField(
        label='',
        widget=forms.TextInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Электронная почта'
        })
    )


class ChangePasswordForm(forms.Form):
    """Форма смены пароля.

    :ivar forms.CharField old_password: Старый пароль
    :ivar forms.CharField new_password: Новый пароль
    """
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Введите пароль',
            'autocomplete': 'new-password'
        })
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Введите пароль',
            'autocomplete': 'new-password'
        })
    )
