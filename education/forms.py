import os

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from education.models import Courses, Lessons, Task, Topic


class AddCourseForm(forms.Form):
    """Форма для добавления нового курса."""
    course_name = forms.CharField(
        label='Название курса',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Введите название курса'
        })
    )


class AddLessonForm(forms.Form):
    """Форма для добавления нового урока."""
    lesson_description = forms.CharField(
        label='Описание урока',
        max_length=1000,
        widget=forms.Textarea(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Введите описание урока',
            'rows': 4
        })
    )

    lesson_file = forms.FileField(
        label='Загрузить файл',
        help_text='Загрузите файл в формате .md',
        validators=[
            FileExtensionValidator(allowed_extensions=['md'])
        ],
        widget=forms.ClearableFileInput(attrs={
            'class': 'auth-form-control',
            'accept': '.md,text/markdown'
        })
    )

    def clean_lesson_file(self):
        file = self.cleaned_data.get('lesson_file')
        if file:
            ext = os.path.splitext(file.name)[1].lower()
            if ext != '.md':
                raise ValidationError('Разрешены только файлы с расширением .md')
        return file


class TopicChoiceForm(forms.Form):
    """Форма для выбора тем курса."""
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
