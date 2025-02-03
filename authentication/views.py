from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.contrib import messages
from authentication.forms import RegisterForm, LoginForm
from main.models import User


class RegisterView(View):
    """
    Классовое представление регистрации.
    """

    @staticmethod
    def get(request):
        """
        Возвращает шаблон для регистрации.
        Используются формы Django.

        :param request:
        :return: Шаблон + форма
        """
        return render(request, 'register.html', {'RegisterForm': RegisterForm})

    @staticmethod
    def post(request):
        """
        Обработчик регистрации аккаунта.
        Получает информацию из формы Django.

        :param request:
        :return: Сообщение об успехе/ошибке
        """
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            repeat_password = form.cleaned_data['repeat_password']

            errors = None

            if password != repeat_password:
                errors = True
                messages.error(request, "Пароли не совпадают")

            if User.objects.filter(email=email).exists():
                errors = True
                messages.error(request, "Пользователь с такой почтой уже зарегистрирован.")

            if errors:
                user = User.objects.create_user(email=email, password=password, username=username)

                login(request, user)

                messages.success(request, "Вы успешно вошли!")

        return render(request, 'register.html')


class LoginView(View):
    """
    Классовое представление входа в аккаунт.
    """

    @staticmethod
    def get(request):
        """
        Возвращает шаблон для входа в аккаунт.
        Используются формы Django.

        :param request:
        :return: Шаблон + форма
        """
        return render(request, 'login.html', {'LoginForm': LoginForm})

    @staticmethod
    def post(request):
        """
        Обработчик входа в аккаунт.
        Получает информацию из формы Django.

        :param request:
        :return: Сообщение об успехе/ошибке
        """
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)
            errors = None

            if user:
                if user.is_active is False:
                    errors = True
                    messages.error(request, "Ваш аккаунт отключён. Обратитесь к администратору.")

                if errors:
                    login(request, user)

                    messages.success(request, "Вы успешно вошли!")
            else:
                messages.error(request, 'Неверный email или пароль.')

        return render(request, 'login.html')
