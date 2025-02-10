# Создание представлений и шаблонов

В этом уроке мы изучим, как создавать представления в Django и использовать шаблоны для отображения данных пользователям. Представления обрабатывают запросы и возвращают ответы, а шаблоны позволяют формировать HTML-код для отображения.

## Шаг 1: Создание представления

Давайте создадим представление для отображения списка книг. Откройте файл `views.py` в папке `myapp` и добавьте следующий код:

```python
from django.shortcuts import render
from .models import Book

def book_list(request):
    books = Book.objects.all()  # Получаем все книги из базы данных
    return render(request, 'myapp/book_list.html', {'books': books})
```

### Описание кода:

- **render**: Функция, которая объединяет шаблон с данными и возвращает HTTP-ответ.
- **Book.objects.all()**: Получает все записи из модели `Book`.
- **'myapp/book_list.html'**: Путь к шаблону, который мы создадим в следующем шаге.

## Шаг 2: Создание шаблона

Теперь создадим шаблон для отображения списка книг. Создайте папку `templates` внутри папки `myapp`, а затем создайте в ней папку `myapp` и файл `book_list.html`:

```
myapp/
    templates/
        myapp/
            book_list.html
```

Откройте файл `book_list.html` и добавьте следующий код:

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
            <li>{{ book.title }} by {{ book.author }} (ISBN: {{ book.isbn }})</li>
        {% empty %}
            <li>Нет книг для отображения.</li>
        {% endfor %}
    </ul>
</body>
</html>
```

### Описание шаблона:

- **{% for book in books %}**: Цикл для перебора всех книг, переданных из представления.
- **{{ book.title }}**: Выводит название книги.
- **{% empty %}**: Отображает сообщение, если список книг пуст.

## Шаг 3: Настройка URL-адресов

Теперь нам нужно связать наше представление с URL-адресом. Откройте файл `urls.py` в папке `myapp` (если его нет, создайте) и добавьте следующий код:

```python
from django.urls import path
from .views import book_list

urlpatterns = [
    path('books/', book_list, name='book_list'),  # URL для списка книг
]
```

Не забудьте подключить URL-адреса вашего приложения в основном файле `urls.py` проекта. Откройте `urls.py` в папке `myproject` и добавьте:

```python
from django.contrib import admin
from django.urls import path, include  # Импортируем include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),  # Подключаем URL-адреса приложения
]
```

## Шаг 4: Запуск сервера и проверка

Теперь, когда все настроено, запустите сервер разработки:

```bash
python manage.py runserver
```

Перейдите в браузере по адресу `http://127.0.0.1:8000/books/`, чтобы увидеть список книг. Если у вас есть книги в базе данных, они должны отображаться на странице!

## Заключение

В этом уроке мы создали представление для отображения списка книг, разработали шаблон для визуализации данных и настроили маршрутизацию URL. Это основа для создания динамических веб-страниц в Django.
