from django.db import models
from authentication.models import User


class UserProfile(models.Model):
    profile_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    about = models.TextField(default='Не указано')
    email = models.TextField(default='Не указано') # Контактный email
    phone = models.TextField(default='Не указано')
