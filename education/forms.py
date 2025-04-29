from django import forms
from education.models import Courses, Lessons, Task, Topic


class AddCourseForm(forms.Form):
    """Форма для добавления нового курса.

    :ivar forms.CharField course_name: Название курса
    """
    course_name = forms.CharField(
        label='Название курса', max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Введите название курса'
        })
    )


class AddLessonForm(forms.Form):
    """Форма для добавления нового урока.

    :ivar forms.CharField lesson_description: Описание урока
    :ivar forms.FileField lesson_file: Загружаемый файл (формат .md)
    """
    lesson_description = forms.CharField(
        label='Описание урока', max_length=1000,
        widget=forms.Textarea(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Введите описание урока',
            'rows': 4
        })
    )
    lesson_file = forms.FileField(
        label='Загрузить файл',
        help_text='Загрузите файл в формате .md',
        widget=forms.ClearableFileInput(attrs={
            'class': 'auth-form-control'
        })
    )


class TopicChoiceForm(forms.Form):
    """Форма для выбора тем курса.

    :ivar forms.ModelMultipleChoiceField topics: Список тем (с возможностью множественного выбора)
    """
    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
