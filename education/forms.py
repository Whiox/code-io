from django import forms

class AddCourseForm(forms.Form):
    """
    Форма для добавления курсов
    """
    course_name = forms.CharField(
        label='Название курса', max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'auth-form-control',
            'placeholder': 'Введите название курса'
        })
    )

class AddLessonForm(forms.Form):
    """
    Форма для добавления урока
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

