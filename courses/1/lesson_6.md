
# Валидация форм и обработка ошибок

В этом уроке мы рассмотрим, как выполнять валидацию данных в формах Django и как обрабатывать ошибки, чтобы обеспечить корректный ввод данных пользователями.

## Шаг 1: Обновление формы с дополнительной валидацией

Давайте добавим валидацию в нашу форму для добавления книг. Откройте файл `forms.py` и добавьте метод `clean` для проверки уникальности ISBN:

```python
from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'published_date', 'isbn']

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if Book.objects.filter(isbn=isbn).exists():
            raise forms.ValidationError("Книга с таким ISBN уже существует.")
        return isbn
```

### Описание кода:

- **clean_isbn**: Метод для проверки уникальности поля ISBN. Если книга с таким ISBN уже существует, выбрасывается ошибка валидации.

## Шаг 2: Обработка ошибок в представлении

Теперь нужно убедиться, что ошибки валидации отображаются в нашем представлении. Обновите файл `views.py` следующим образом:

```python
from django.shortcuts import render, redirect
from .forms import BookForm

def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем книгу в базе данных
            return redirect('book_list')
    else:
        form = BookForm()  # Создаем пустую форму

    return render(request, 'myapp/add_book.html', {'form': form})
```

Ошибки будут автоматически добавляться к форме, если валидация не пройдет.

## Шаг 3: Обновление шаблона для отображения ошибок

Теперь обновим шаблон `add_book.html`, чтобы отображать ошибки валидации. Измените файл следующим образом:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Добавить книгу</title>
</head>
<body>
    <h1>Добавить книгу</h1>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}  <!-- Отображаем форму -->
        <button type="submit">Сохранить</button>
    </form>
    <a href="{% url 'book_list' %}">Назад к списку книг</a>

    {% if form.errors %}
        <ul>
            {% for field, errors in form.errors.items %}
                <li>{{ field }}: {{ errors|join:", " }}</li>
            {% endfor %}
        </ul>
    {% endif %}
</body>
</html>
```

### Описание изменений:

- **{% if form.errors %}**: Проверяем, есть ли ошибки в форме.
- **{{ field }}: {{ errors|join:", " }}**: Отображаем ошибки для каждого поля.

## Шаг 4: Проверка работы валидации

Запустите сервер разработки:

```bash
python manage.py runserver
```

Перейдите в браузере по адресу `http://127.0.0.1:8000/books/add/`. Попробуйте добавить книгу с существующим ISBN. Вы должны увидеть сообщение об ошибке, указывающее на то, что книга с таким ISBN уже существует.

## Заключение

В этом уроке мы научились добавлять валидацию в формы Django и обрабатывать ошибки, чтобы улучшить взаимодействие с пользователями. Валидация данных — важный аспект разработки веб-приложений, который помогает предотвратить ошибки и обеспечивает корректный ввод информации.
