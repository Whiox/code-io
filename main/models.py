from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager
)

from django.contrib.auth.hashers import (
    make_password,
    check_password
)

# Пользователи
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser ):
    name = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()  # Исправлено имя на UserManager

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

# Курсы
class Course(models.Model):
    course_id = models.AutoField(primary_key=True)  # Автоинкрементный ID курса
    additional_info = models.TextField(blank=True)  # Дополнительная информация о курсе

    def __str__(self):
        return f"Course {self.course_id}"

class Curriculum(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)  # Исправлено на ForeignKey к модели User
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # Связь с курсом
    additional_info = models.TextField(blank=True)  # Дополнительная информация о учебном плане

    def __str__(self):
        return f"Curriculum for Student {self.student.email} in Course {self.course.course_id}"

class Task(models.Model):
    task_id = models.AutoField(primary_key=True)  # Автоинкрементный ID задачи
    correct_answer = models.TextField()  # Правильный ответ на задачу

    def __str__(self):
        return f"Task {self.task_id}"

class UserProgress(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # Связь с курсом
    lesson_id = models.IntegerField()  # ID урока
    task = models.ForeignKey(Task, on_delete=models.CASCADE)  # Исправлено на ForeignKey к модели Task
    task_solved = models.BooleanField(default=False)  # Решил ли пользователь задачу

    def __str__(self):
        return f"Progress of Student in Course {self.course.course_id}, Lesson {self.lesson_id}, Task {self.task.task_id}"
