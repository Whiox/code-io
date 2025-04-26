from django.db import models
from authentication.models import User


class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Courses(models.Model):
    course_id = models.AutoField(primary_key=True)
    title = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='my_courses')
    topics = models.ManyToManyField(Topic, related_name='courses', blank=True)


class Lessons(models.Model):
    lesson_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    title = models.TextField()


class Task(models.Model):
    tusk_id = models.AutoField(primary_key=True)
    lesson = models.ForeignKey(Lessons, on_delete=models.CASCADE)


class Stars(models.Model):
    course = models.ForeignKey(
        Courses,
        on_delete=models.CASCADE,
        related_name='stars'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.IntegerField(default=0)
