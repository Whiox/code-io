
# Работа с формами и обработка пользовательского ввода

В этом уроке мы изучим, как создавать формы в Django и обрабатывать пользовательский ввод. Формы позволяют пользователям взаимодействовать с вашим приложением, отправляя данные, такие как комментарии, отзывы или регистрационные данные.

## Шаг 1: Создание формы

Для начала создадим форму для добавления новых книг. В папке `myapp` создайте файл `forms.py` и добавьте следующий код:

```python
from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'published_date', 'isbn']
```

### Описание кода:

- **forms.ModelForm**: Класс, который автоматически создает форму на основе модели.
- **fields**: Указывает, какие поля из модели будут включены в форму.

## Шаг 2: Создание представления для обработки формы

Теперь создадим представление, которое будет обрабатывать форму. Откройте файл `views.py` и добавьте следующее представление:

```python
from django.shortcuts import render, redirect
from .forms import BookForm

def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем книгу в базе данных
            return redirect('book_list')  # Перенаправляем на страницу со списком книг
    else:
        form = BookForm()  # Создаем пустую форму

    return render(request, 'myapp/add_book.html', {'form': form})
```

### Описание кода:

- **request.method**: Проверяем, был ли запрос методом POST (т.е. форма была отправлена).
- **form.is_valid()**: Проверяем, корректны ли данные в форме.
- **form.save()**: Сохраняем данные в базе данных.
- **redirect('book_list')**: Перенаправляем пользователя на страницу со списком книг после успешного добавления.

## Шаг 3: Создание шаблона для формы

Создайте новый файл `add_book.html` в папке `templates/myapp/` и добавьте следующий код:

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
</body>
</html>
```

### Описание шаблона:

- **{% csrf_token %}**: Защита от межсайтовой подделки запросов (CSRF).
- **{{ form.as_p }}**: Отображает форму в виде параграфов.

## Шаг 4: Настройка URL-адресов

Теперь добавим новый маршрут для нашего представления. Откройте файл `urls.py` в папке `myapp` и добавьте следующий код:

```python
from django.urls import path
from .views import book_list, add_book

urlpatterns = [
    path('books/', book_list, name='book_list'),
    path('books/add/', add_book, name='add_book'),  # URL для добавления книги
]
```

## Шаг 5: Запуск сервера и проверка

Запустите сервер разработки:

```bash
python manage.py runserver
```

Перейдите в браузере по адресу `http://127.0.0.1:8000/books/add/`, чтобы увидеть форму для добавления новой книги. Заполните форму и отправьте данные. После этого вы должны быть перенаправлены на страницу со списком книг, где новая книга будет отображаться.

## Заключение

В этом уроке мы научились создавать формы в Django, обрабатывать пользовательский ввод и сохранять данные в базе данных. Формы — это мощный инструмент для взаимодействия с пользователями и получения информации.
