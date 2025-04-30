from django.db import models
from authentication.models import User


class Topic(models.Model):
    """Модель для представления темы курса.

    :ivar models.CharField name: Название темы (макс. 100 символов)
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Courses(models.Model):
    """Модель курса.

    :ivar models.AutoField course_id: Уникальный идентификатор курса
    :ivar models.TextField title: Название курса
    :ivar models.ForeignKey author: Автор курса (пользователь)
    :ivar models.ManyToManyField topics: Темы, связанные с курсом
    """
    course_id = models.AutoField(primary_key=True)
    title = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='my_courses')
    topics = models.ManyToManyField(Topic, related_name='courses', blank=True)


class Lessons(models.Model):
    """Модель урока.

    :ivar models.AutoField lesson_id: Уникальный идентификатор урока
    :ivar models.ForeignKey course: Курс, к которому относится урок
    :ivar models.TextField title: Название урока
    """
    lesson_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    title = models.TextField()


class Task(models.Model):
    """Модель задания.

    :ivar models.AutoField tusk_id: Уникальный идентификатор задания
    :ivar models.ForeignKey lesson: Урок, к которому относится задание
    """
    tusk_id = models.AutoField(primary_key=True)
    lesson = models.ForeignKey(Lessons, on_delete=models.CASCADE)


class Stars(models.Model):
    """Модель оценки курса пользователем.

    :ivar models.ForeignKey course: Курс, которому дана оценка
    :ivar models.ForeignKey user: Пользователь, поставивший оценку
    :ivar models.IntegerField data: Числовое значение оценки (по умолчанию 0)
    """
    course = models.ForeignKey(
        Courses,
        on_delete=models.CASCADE,
        related_name='stars'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.IntegerField(default=0)


class Report(models.Model):
    """Модель жалобы на курс

    :ivar models.ForeignKey course: Курс, на который была подана жалоба
    :ivar models.ForeignKey user: Пользователь, подавший жалобу
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    course = models.ForeignKey(
        Courses,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    reason = models.TextField()

