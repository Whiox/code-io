from django.db import models
from main.models import User


class ResetRequest(models.Model):
    request_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.TextField()
    browser = models.TextField()
    browser_version = models.TextField()
    os = models.TextField()
    os_version = models.TextField()
    device = models.TextField()
