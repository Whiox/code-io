from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.urls import reverse
from django.contrib import messages
from authentication.forms import RegisterForm, LoginForm, ResetPasswordForm, ChangePasswordForm
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from authentication.methods import generate_password, user_info_view, is_author
from authentication.models import ResetRequest
from django.core.mail import send_mail
from main.models import User
import secrets


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

            if errors is None:
                user = User.objects.create_user(email=email, password=password, username=username)

                send_mail(
                    subject="Добро пожаловать!",
                    message=f"Вы зарегистрировались на сайте",
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
    """
    Классовое представления выхода из аккаунта
    """

    @staticmethod
    def get(request):
        """
        Обработчик выхода из аккаунта.

        :param request:
        :return: Перенаправляет на главную страницу.
        """
        logout(request)

        return redirect('/')


class ResetPasswordView(View):
    """
    Классовое представление сброса пароля
    """

    @staticmethod
    def get(request):
        """
        Возвращает шаблон для сброса пароля.
        Используются формы Django.

        :param request:
        :return: Шаблон + форма
        """
        return render(request, 'reset.html', {'ResetPasswordForm': ResetPasswordForm})

    @staticmethod
    def post(request):
        """
        Обработчик сброса.
        Получает информацию из формы Django.
        Отправляет пользователю случайную ссылку для сброса пароля.

        :param request:
        :return: Сообщение об успехе/ошибке
        """
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()

            if user:
                info = user_info_view(request)

                token = secrets.token_urlsafe(32)

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
    """
    Обрабатывает переход по ссылке сброса пароля.
    """

    @staticmethod
    def get(request, token):
        """
        Генерирует новый пароль и отправляет его пользователю на его почту.

        :param request:
        :param token: Уникальная ссылка
        :return: Перенаправление на страницу входа
        """
        reset_request = ResetRequest.objects.filter(url=token).first()

        if not reset_request:
            messages.error(request, "Недействительная или устаревшая ссылка для сброса пароля.")
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
            messages.error(request, "Вы должны осуществлять все действия с одного устройства")

        return render(request, 'reset.html', {'ResetPasswordForm': ResetPasswordForm()})


class ChangePasswordView(View):
    """
    Классовое представление смены пароля
    """

    @staticmethod
    def get(request):
        """
        Возвращает шаблон для смены пароля.
        Используются формы Django.

        :param request:
        :return: Шаблон + форма
        """
        return render(request, 'change.html', {'ChangePasswordForm': ChangePasswordForm})

    @staticmethod
    def post(request):
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
