from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.urls import reverse
from django.contrib import messages
from authentication.forms import RegisterForm, LoginForm, ResetPasswordForm, ChangePasswordForm
from authentication.methods import generate_password, user_info_view, is_author
from authentication.models import ResetRequest
from django.core.mail import send_mail
from authentication.models import User
import secrets


class RegisterView(View):
    """
    Регистрация.
    """

    @staticmethod
    def get(request):
        """
        Возвращает шаблон для регистрации.
        Используются формы Django.

        :param request: HTTP Django request
        :return: render: register.html + RegisterForm
        """
        return render(request, 'register.html', {'RegisterForm': RegisterForm})

    @staticmethod
    def post(request):
        """
        Создаёт аккаунт для пользователя.
        Получает информацию из формы Django.
        Отправляет Email с информацией о регистрации.

        :param request: HTTP Django request
        :return: render: register.html + RegisterForm
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
    """
    Вход в аккаунт.
    """

    @staticmethod
    def get(request):
        """
        Возвращает шаблон для входа в аккаунт.
        Отправляет форму Django.

        :param request: HTTP Django request
        :return: render: login.html + LoginForm
        """
        return render(request, 'login.html', {'LoginForm': LoginForm})

    @staticmethod
    def post(request):
        """
        Обработчик входа в аккаунт.
        Получает информацию из формы Django.

        :param request: HTTP Django request
        :return: render: login.html + LoginForm + message
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
    Выход из аккаунта.
    """

    @staticmethod
    def get(request):
        """
        Обработчик выхода из аккаунта.

        :param request: HTTP Django request
        :return: redirect: '/'
        """
        if request.user.is_anonymous:
            return redirect("/login/")

        logout(request)

        return redirect('/')


class ResetPasswordView(View):
    """
    Сброс пароля.
    """

    @staticmethod
    def get(request):
        """
        Возвращает шаблон для сброса пароля.
        Отправляет форму Django.

        :param request: HTTP Django request
        :return: render: reset.html + ResetPasswordForm
        """
        return render(request, 'reset.html', {'ResetPasswordForm': ResetPasswordForm})

    @staticmethod
    def post(request):
        """
        Отправляет пользователю на Email ссылку на подтверждения сброса.
        Email пользователя получается из формы.
        Для генерации ссылки используется secrets.
        Сохраняет данные о текущем устройстве пользователя.

        :param request: HTTP Django request
        :return: render: reset.html + ResetPasswordForm + message
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
        Генерируемый пароль имеет формат XXX-XXX-XXX, где X - любой символ.
        Проверяет устройство с которого был отправлен запрос на сброс и текущее.

        :param request: HTTP Django request.
        :param token: Уникальная ссылка, отправленная пользователю на Email
        :return: render: reset.html + ResetPasswordForm + message
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
    Смена пароля.
    """

    @staticmethod
    def get(request):
        """
        Возвращает шаблон для смены пароля.
        Отправляет форму Django.

        :param request: HTTP Django request
        :return: render: change.html + ChangePasswordForm
        """
        if request.user.is_anonymous:
            return redirect("/login/")

        return render(request, 'change.html', {'ChangePasswordForm': ChangePasswordForm})

    @staticmethod
    def post(request):
        """
        Получает старый и новый пароль из формы Django.
        В случае совпадения старого и текущего пароля, изменяет пароль на новый.
        Отправляет Email пользователю о смене пароля.

        :param request: HTTP Django request
        :return: render: change.html + ChangePasswordForm + message
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
