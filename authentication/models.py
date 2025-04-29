"""Модели пользователей и запросов на сброс пароля."""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password, check_password


class UserManager(BaseUserManager):
    """Менеджер пользовательской модели.

    Предоставляет методы для создания пользователей и суперпользователей.
    """

    def create_user(self, email, password=None, **extra_fields):
        """Создает обычного пользователя.

        :param str email: Адрес электронной почты
        :param str password: Пароль (по умолчанию None)
        :param extra_fields: Дополнительные поля модели
        :return: Созданный пользователь
        :rtype: User
        :raises ValueError: Если email не указан
        """
        if not email:
            raise ValueError('Email должен быть указан')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Создает суперпользователя.

        :param str email: Адрес электронной почты
        :param str password: Пароль
        :param extra_fields: Дополнительные поля
        :return: Созданный суперпользователь
        :rtype: User
        :raises ValueError: Если is_staff или is_superuser не установлены
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Пользовательская модель.

    Используется для аутентификации по email.

    :ivar str username: Имя пользователя
    :ivar str email: Уникальный email пользователя
    :ivar str theme: Тема интерфейса (по умолчанию 'light')
    :ivar bool is_active: Активен ли пользователь
    :ivar bool wait_for_activate: Ожидает ли пользователь активации
    :ivar bool is_staff: Персонал (доступ в админку)
    :ivar UserManager objects: Менеджер модели
    """

    username = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    theme = models.TextField(default='light')
    is_active = models.BooleanField(default=True)
    wait_for_activate = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self) -> str:
        """Возвращает email пользователя."""
        return str(self.email)

    def set_password(self, raw_password):
        """Устанавливает хэшированный пароль.

        :param str raw_password: Пароль в открытом виде
        """
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Проверяет правильность пароля.

        :param str raw_password: Пароль в открытом виде
        :return: True, если пароль верен
        :rtype: bool
        """
        return check_password(raw_password, self.password)

    def get_username(self):
        """Возвращает имя пользователя.

        :return: username
        :rtype: str
        """
        return self.username


class ResetRequest(models.Model):
    """Модель запроса на сброс пароля.

    :ivar int request_id: Уникальный идентификатор запроса
    :ivar User user: Пользователь, создавший запрос
    :ivar str url: Уникальная ссылка для сброса
    :ivar str ip: IP-адрес отправителя
    :ivar str browser: Название браузера
    :ivar str browser_version: Версия браузера
    :ivar str os: Название операционной системы
    :ivar str os_version: Версия операционной системы
    :ivar str device: Тип устройства (например, desktop/mobile)
    """

    request_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.TextField()
    ip = models.TextField()
    browser = models.TextField()
    browser_version = models.TextField()
    os = models.TextField()
    os_version = models.TextField()
    device = models.TextField()
