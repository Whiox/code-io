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
    email = forms.CharField(
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

    :param auth: Имя пользователя или электронная почта
    :param password: Пароль
    """
    auth = forms.CharField(
        label='', max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Имя пользователя или электронная почта'
        })
    )
    password = forms.CharField(
        label='', max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Пароль'
            })
        )