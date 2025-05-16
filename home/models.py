from django.db import models
from authentication.models import User


class UserProfile(models.Model):
    """Модель профиля пользователя.

    :ivar models.AutoField profile_id: Уникальный идентификатор профиля
    :ivar models.ForeignKey user: Пользователь, к которому относится профиль
    :ivar models.TextField about: Краткая информация о пользователе (по умолчанию "Не указано")
    :ivar models.EmailField email: Контактный email пользователя (по умолчанию "Null")
    """
    profile_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )
    about = models.TextField(default='Не указано')
    email = models.EmailField(blank=True)


class SocialNetwork(models.Model):
    """Модель социальной сети, связанной с профилем пользователя.

    :ivar models.AutoField network_id: Уникальный идентификатор записи
    :ivar models.ForeignKey user_profile: Профиль пользователя, к которому привязана сеть
    :ivar models.TextField label: Название или тип социальной сети (например, Telegram, VK)
    :ivar models.TextField linc: Ссылка на профиль пользователя в социальной сети
    """
    network_id = models.AutoField(primary_key=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    label = models.TextField(null=False)
    linc = models.TextField(null=False)


class Technology(models.Model):
    """Модель технологий пользователя.

    :ivar models.AutoField interest_id: Уникальный идентификатор технологии
    :ivar models.ForeignKey user_profile: Профиль пользователя, к которому относится интерес
    :ivar models.TextField label: Название технологии (например, Django, Go)
    """
    interest_id = models.AutoField(primary_key=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    label = models.TextField(null=False)
