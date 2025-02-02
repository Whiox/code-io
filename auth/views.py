from django.shortcuts import render

from django.views import (
    View
)

from django.contrib import (
    messages
)

from main.models import (
    User
)


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
        return render(request, 'register.html')

    @staticmethod
    def post(request):
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repeat_password = request.POST.get('repeat_password')

        errors = None

        if password != repeat_password:
            errors = True
            messages.error(request, "Пароли не совпадают")

        if Users.objects.filter(email=email).exists():
            errors = True
            messages.error(request, "Пользователь с такой почтой уже зарегистрирован.")

        if errors is None:
            user = Users.objects.create_user(email=email, password=password, name=name)

            login(request, user)

            messages.success(request, "Вы успешно вошли!")

            Notifications.objects.create(
                user_id=request.user, type='welcome', title="Добро пожаловать", text=f"Ваш аккаунт создан: {email}"
            )

        return render(request, 'register.html')


class LoginView(View):
    @staticmethod
    def get(request):
        return render(request, 'login.html')

    @staticmethod
    def post(request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        errors = None

        if user:
            if user.is_active is False:
                errors = True
                messages.error(request, "Ваш аккаунт отключён. Обратитесь к администратору.")

            if errors is None:
                login(request, user)

                messages.success(request, "Вы успешно вошли!")

                Notifications.objects.create(
                    user_id=request.user, type='welcome', title="Добро пожаловать", text=f"Вы вошли в аккаунт: {email}"
                )
        else:
            messages.error(request, 'Неверный email или пароль.')

        return render(request, 'login.html')
