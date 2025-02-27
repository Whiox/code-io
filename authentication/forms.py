from django import forms


class RegisterForm(forms.Form):
    """
    Форма для регистрации

    :param username: Имя пользователя
    :param email: Электронная почта пользователя
    :param password: Пароль
    :param repeat_password: Повтор пароля
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
        label='', max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Введите пароль'
        })
    )
    repeat_password = forms.CharField(
        label='', max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Повторите пароль'
            })
        )


class LoginForm(forms.Form):
    """
    Форма для входа в аккаунт

    :param email: Электронная почта
    :param password: Пароль
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
    """
    Форма для входа в аккаунт

    :param email: Электронная почта
    """
    email = forms.EmailField(
        label='',
        widget=forms.TextInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Электронная почта'
        })
    )


class ChangePasswordForm(forms.Form):
    """
    Форма для сброса пароля

    :param old_password: Старый пароль
    :param new_password: Новый пароль
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
