from django.db import models
from authentication.models import User


class UserProfile(models.Model):
    profile_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    about = models.TextField(default='Не указано')
    email = models.TextField(default='Не указано') # Контактный email
    phone = models.TextField(default='Не указано')


class SocialNetwork(models.Model):
    network_id = models.AutoField(primary_key=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    label = models.TextField(null=False)
    linc = models.TextField(null=False)


class Interest(models.Model):
    interest_id = models.AutoField(primary_key=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    label = models.TextField(null=False)
