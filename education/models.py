from django.db import models
from authentication.models import User


class Topic(models.Model):
    """Модель темы курса.

    :ivar models.CharField name: Название темы (максимум 100 символов)
    :ivar models.ForeignKey author: Автор темы (пользователь, опционально)
    :ivar models.DateTimeField created_at: Дата создания (автоматически)
    """
    name = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

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
    topics = models.ManyToManyField(
        Topic,
        related_name='courses',
        blank=True,
        verbose_name='Темы курса'
    )


class Lessons(models.Model):
    """Модель урока.

    :ivar models.AutoField lesson_id: Уникальный идентификатор урока
    :ivar models.ForeignKey course: Курс, к которому относится урок
    :ivar models.TextField title: Название урока
    """
    lesson_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    title = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ('course', 'order')
        ordering = ['order']


class CourseProgress(models.Model):
    """Модель прогресса для курса

    :ivar models.ForeignKey user: Пользователь
    :ivar models.ForeignKey lesson: Урок
    :ivar models.BooleanField status: Статус выполнения
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lessons, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)


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


class ReportCourse(models.Model):
    """Модель жалобы на курс.

    :ivar models.ForeignKey author: Автор жалобы (пользователь)
    :ivar models.ForeignKey course: Курс, на который подана жалоба
    :ivar models.TextField reason: Текстовое описание причины жалобы
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


class ReportTopic(models.Model):
    """Модель жалобы на тему курса.

    :ivar models.ForeignKey course: Курс, к которому относится тема
    :ivar models.ForeignKey author: Автор жалобы (пользователь)
    :ivar models.CharField reason: Причина жалобы (варианты выбора)
    :ivar models.DateTimeField created_at: Дата создания жалобы (автоматически)
    """
    REASON_CHOICES = [
        ('spam', 'Спам'),
        ('illegal', 'Незаконно'),
        ('Unacceptable', 'Недопустимо')
    ]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='reports', verbose_name='Тег')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(
        max_length=50,
        choices=REASON_CHOICES,
        verbose_name='Причина жалобы'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def __str__(self):
        return f"Жалоба на курс {self.course_id} ({self.reason})"
