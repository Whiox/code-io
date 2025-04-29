"""Представления для аутентификации в формате классов.

Каждый класс реализует обработку HTTP-запросов для соответствующих действий:
регистрация, вход, выход, сброс и смена пароля.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.urls import reverse
from django.contrib import messages
from authentication.forms import (
    RegisterForm, LoginForm,
    ResetPasswordForm, ChangePasswordForm
)
from authentication.methods import (
    generate_password, user_info_view, is_author
)
from authentication.models import ResetRequest, User
from django.core.mail import send_mail
from secrets import token_urlsafe


class RegisterView(View):
    """Регистрация нового пользователя.

    :cvar get: Отображает форму регистрации.
    :cvar post: Обрабатывает создание аккаунта, отправку email и вход.
    """

    @staticmethod
    def get(request):
        """
        Возвращает шаблон регистрации с формой.

        :param request: HTTP Django request
        :return: render: register.html + RegisterForm
        """
        return render(request, 'register.html', {'RegisterForm': RegisterForm})

    @staticmethod
    def post(request):
        """
        Обрабатывает данные формы регистрации.

        Создает пользователя, отправляет приветственный email и выполняет вход.

        :param request: HTTP Django request
        :return: render: register.html + RegisterForm (с сообщениями)
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

            if errors is None:
                user = User.objects.create_user(
                    email=email, password=password, username=username
                )
                send_mail(
                    subject="Добро пожаловать!",
                    message="Вы зарегистрировались на сайте",
                    from_email="code-io.no-reply@yandex.ru",
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                login(request, user)
                messages.success(request, "Вы успешно вошли!")
        else:
            messages.error(request, "Форма заполнена неправильно")

        return render(request, 'register.html', {'RegisterForm': RegisterForm})


class LoginView(View):
    """Вход пользователя в аккаунт.

    :cvar get: Отображает форму входа.
    :cvar post: Обрабатывает аутентификацию и вход.
    """

    @staticmethod
    def get(request):
        """
        Возвращает шаблон входа с формой.

        :param request: HTTP Django request
        :return: render: login.html + LoginForm
        """
        return render(request, 'login.html', {'LoginForm': LoginForm})

    @staticmethod
    def post(request):
        """
        Обрабатывает данные формы входа.

        Выполняет аутентификацию, вход и выводит сообщения об ошибках.

        :param request: HTTP Django request
        :return: render: login.html + LoginForm (с сообщениями) или redirect на главную
        """
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)
            if user is not None:
                if not user.is_active:
                    messages.error(request, "Ваш аккаунт отключён. Обратитесь к администратору.")
                else:
                    login(request, user)
                    messages.success(request, "Вы успешно вошли!")
                    return redirect('/')
            else:
                messages.error(request, "Такого пользователя не существует.")
        else:
            messages.error(request, "Форма заполнена неправильно")

        return render(request, 'login.html', {'LoginForm': LoginForm})


class LogoutView(View):
    """Выход пользователя из аккаунта.

    :cvar get: Обрабатывает logout и редиректит на страницу входа.
    """

    @staticmethod
    def get(request):
        """
        Выполняет выход пользователя.

        :param request: HTTP Django request
        :return: redirect: '/login/'
        """
        if request.user.is_anonymous:
            return redirect("/login/")
        logout(request)
        return redirect('/')


class ResetPasswordView(View):
    """Инициация процедуры сброса пароля.

    :cvar get: Отображает форму для запроса ссылки сброса.
    :cvar post: Генерирует токен, сохраняет запрос и шлет email.
    """

    @staticmethod
    def get(request):
        """
        Возвращает форму запроса сброса пароля.

        :param request: HTTP Django request
        :return: render: reset.html + ResetPasswordForm
        """
        return render(request, 'reset.html', {'ResetPasswordForm': ResetPasswordForm})

    @staticmethod
    def post(request):
        """
        Обрабатывает форму запроса сброса пароля.

        Сохраняет метаданные запроса и отправляет email со ссылкой.

        :param request: HTTP Django request
        :return: render: reset.html + ResetPasswordForm (с сообщениями)
        """
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()

            if user:
                info = user_info_view(request)
                token = token_urlsafe(32)
                reset_request = ResetRequest.objects.create(
                    user=user, url=token, **info
                )
                reset_link = request.build_absolute_uri(
                    reverse('reset_password_confirm', kwargs={'token': reset_request.url})
                )
                send_mail(
                    subject="Восстановление пароля",
                    message=f"Перейдите по ссылке, чтобы сбросить пароль: {reset_link}",
                    from_email="code-io.no-reply@yandex.ru",
                    recipient_list=[email],
                    fail_silently=False,
                )
                messages.success(request, "Ссылка для сброса пароля отправлена на почту.")
            else:
                messages.error(request, "Пользователь с таким email не найден.")
        else:
            messages.error(request, "Форма заполнена неправильно")

        return render(request, 'reset.html', {'ResetPasswordForm': ResetPasswordForm()})


class ResetPasswordConfirmView(View):
    """Подтверждение сброса пароля по токену.

    :cvar get: Генерирует новый пароль и отправляет пользователю.
    """

    @staticmethod
    def get(request, token):
        """
        Заканчивает процесс сброса пароля.

        Проверяет токен и устройство, генерирует новый пароль.

        :param request: HTTP Django request
        :param str token: Уникальный токен сброса
        :return: render: reset.html + ResetPasswordForm (с сообщениями)
        """
        reset_request = ResetRequest.objects.filter(url=token).first()
        if not reset_request:
            messages.error(
                request,
                "Недействительная или устаревшая ссылка для сброса пароля."
            )
            return render(request, 'reset.html', {'ResetPasswordForm': ResetPasswordForm()})

        user = reset_request.user
        if is_author(request, reset_request):
            new_password = generate_password()
            user.set_password(new_password)
            user.save()
            send_mail(
                subject="Ваш новый пароль",
                message=f"Ваш новый пароль: {new_password}",
                from_email="code-io.no-reply@yandex.ru",
                recipient_list=[user.email],
                fail_silently=False,
            )
            reset_request.delete()
            messages.success(request, "Новый пароль отправлен вам на почту.")
        else:
            messages.error(
                request,
                "Вы должны осуществлять все действия с одного устройства"
            )

        return render(request, 'reset.html', {'ResetPasswordForm': ResetPasswordForm()})


class ChangePasswordView(View):
    """Смена текущего пароля пользователя.

    :cvar get: Отображает форму смены пароля.
    :cvar post: Обрабатывает смену и отправляет уведомление по email.
    """

    @staticmethod
    def get(request):
        """
        Возвращает форму смены пароля.

        :param request: HTTP Django request
        :return: redirect: '/login/' если не авторизован или render: change.html
        """
        if request.user.is_anonymous:
            return redirect("/login/")
        return render(request, 'change.html', {'ChangePasswordForm': ChangePasswordForm})

    @staticmethod
    def post(request):
        """
        Обрабатывает форму смены пароля.

        Проверяет старый пароль, сохраняет новый и шлет уведомление по email.

        :param request: HTTP Django request
        :return: render: change.html + ChangePasswordForm (с сообщениями)
        """
        if request.user.is_anonymous:
            return redirect("/login/")

        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            if request.user.check_password(old_password):
                request.user.set_password(new_password)
                send_mail(
                    subject="Ваш пароль был изменён",
                    message=f"Ваш новый пароль: {new_password}",
                    from_email="code-io.no-reply@yandex.ru",
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )
                messages.success(request, "Пароль успешно изменён")
            else:
                messages.error(request, "Старый пароль не совпадает")
        else:
            messages.error(request, "Форма заполнена неправильно")

        return render(request, 'change.html', {'ChangePasswordForm': ChangePasswordForm})
