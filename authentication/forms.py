"""Формы аутентификации."""

from django import forms


class RegisterForm(forms.Form):
    """Форма для регистрации нового пользователя.

    :ivar forms.CharField username: Имя пользователя
    :ivar forms.EmailField email: Электронная почта пользователя
    :ivar forms.CharField password: Пароль
    :ivar forms.CharField repeat_password: Повтор пароля
    """
    username = forms.CharField(
        label='', max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Введите имя пользователя'
        })
    )
    email = forms.EmailField(
        label='',
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
    repeat_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Повторите пароль',
            'autocomplete': 'new-password'
        })
    )


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
        label='', max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Пароль'
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
        label='', max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Старый пароль'
        })
    )
    new_password = forms.CharField(
        label='', max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Новый пароль'
        })
    )
