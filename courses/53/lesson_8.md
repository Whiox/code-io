
# Формы и обработка данных

В этом уроке мы изучим, как создавать формы в Django для обработки пользовательских данных. Мы научимся как отображать формы, валидировать данные и сохранять их в базе данных.

## Шаг 1: Создание формы

Для начала создадим форму для добавления новой книги. Создайте файл `forms.py` в вашем приложении и добавьте следующий код:

```python
from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'published_date', 'isbn']
```

### Описание кода:

- **forms.ModelForm**: Класс для создания формы на основе модели.
- **Meta**: Вложенный класс, который указывает модель и поля, которые будут включены в форму.

## Шаг 2: Обновление представления для обработки формы

Теперь обновим представление `book_list` для обработки формы добавления книги. Откройте файл `views.py` и добавьте следующий код:

```python
from django.shortcuts import render, redirect
from .models import Book
from .forms import BookForm

def book_list(request):
    books = Book.objects.all()
    
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем новую книгу в базе данных
            return redirect('book_list')  # Перенаправляем на страницу списка книг
    else:
        form = BookForm()

    return render(request, 'myapp/book_list.html', {'books': books, 'form': form})
```

### Описание кода:

- **request.method == 'POST'**: Проверяем, была ли отправлена форма.
- **form.is_valid()**: Проверяем, валидны ли данные формы.
- **form.save()**: Сохраняем данные в базе данных.
- **redirect('book_list')**: Перенаправляем пользователя на страницу списка книг после успешного добавления.

## Шаг 3: Обновление шаблона

Теперь обновим шаблон `book_list.html`, чтобы отобразить форму. Замените содержимое файла на следующее:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Список книг</title>
</head>
<body>
    <h1>Список книг</h1>
    <ul>
        {% for book in books %}
            <li>{{ book.title }} - {{ book.author }} ({{ book.published_date }})</li>
        {% empty %}
            <li>Книги не найдены.</li>
        {% endfor %}
    </ul>

    <h2>Добавить новую книгу</h2>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}  <!-- Отображение формы -->
        <button type="submit">Добавить книгу</button>
    </form>
</body>
</html>
```

### Описание кода:

- **{% csrf_token %}**: Защита от межсайтовой подделки запросов.
- **{{ form.as_p }}**: Отображает форму в виде параграфов.

## Шаг 4: Проверка работы

Запустите сервер разработки, если он еще не запущен:

```bash
python manage.py runserver
```

Перейдите в браузере по адресу `http://127.0.0.1:8000/books/`. Вы увидите список книг и форму для добавления новой книги. Заполните форму и нажмите кнопку "Добавить книгу". После успешного добавления вы будете перенаправлены на страницу со списком книг.

## Заключение

В этом уроке мы научились создавать и обрабатывать формы в Django, включая валидацию данных и сохранение их в базе данных. Формы являются важной частью взаимодействия с пользователями в веб-приложениях.
