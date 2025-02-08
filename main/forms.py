# courses/forms.py
from django import forms
from .models import Course, Lesson, Task
from django.forms import inlineformset_factory

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content']

LessonFormSet = inlineformset_factory(Course, Lesson, form=LessonForm, extra=1)

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'content','correct_answer']

TaskFormSet = inlineformset_factory(Lesson, Task, form=TaskForm, extra=1)
