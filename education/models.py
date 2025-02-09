from django.db import models
from authentication.models import User


class Courses(models.Model):
    course_id = models.AutoField(primary_key=True)
    title = models.TextField()
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)


class Lessons(models.Model):
    lesson_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    title = models.TextField()


class Task(models.Model):
    tusk_id = models.AutoField(primary_key=True)
    lesson = models.ForeignKey(Lessons, on_delete=models.CASCADE)
