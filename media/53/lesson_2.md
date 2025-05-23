


# Создание моделей и работа с базой данных

В этом уроке мы рассмотрим, как создавать модели в Django и работать с базой данных. Модели представляют собой структуру данных вашего приложения и позволяют взаимодействовать с базой данных.

## Шаг 1: Настройка базы данных

По умолчанию Django использует SQLite в качестве базы данных. Вы можете изменить настройки базы данных в файле `settings.py`. Найдите раздел `DATABASES` и измените его при необходимости. Например, для использования PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydatabase',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```

Не забудьте установить необходимые библиотеки для работы с PostgreSQL:

```bash
pip install psycopg2
```

## Шаг 2: Создание модели

Давайте создадим простую модель для хранения информации о книгах. Откройте файл `models.py` в папке `myapp` и добавьте следующий код:

```python
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    published_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)

    def __str__(self):
        return f"{self.title} by {self.author}"
```

### Описание полей модели:

- **title**: Название книги (строка, максимум 100 символов).
- **author**: Автор книги (строка, максимум 100 символов).
- **published_date**: Дата публикации книги.
- **isbn**: Уникальный идентификатор книги (строка, максимум 13 символов).

## Шаг 3: Создание и применение миграций

После создания модели нам нужно создать миграции и применить их к базе данных. В терминале выполните следующие команды:

```bash
python manage.py makemigrations
python manage.py migrate
```

Эти команды создадут необходимые таблицы в базе данных на основе вашей модели.

## Шаг 4: Работа с моделями в Django Shell

Django предоставляет удобный интерфейс для работы с моделями через оболочку. Запустите оболочку с помощью команды:

```bash
python manage.py shell
```

Теперь вы можете выполнять операции с вашей моделью. Например, добавим новую книгу:

```python
from myapp.models import Book

# Создание новой книги
new_book = Book(title="1984", author="George Orwell", published_date="1949-06-08", isbn="9780451524935")
new_book.save()

# Получение всех книг
books = Book.objects.all()
for book in books:
    print(book)
```

## Шаг 5: Регистрация модели в админке

Чтобы управлять моделями через административную панель, откройте файл `admin.py` в папке `myapp` и добавьте следующий код:

```python
from django.contrib import admin
from .models import Book

admin.site.register(Book)
```

Теперь, когда вы перейдете в административную панель (обычно по адресу `http://127.0.0.1:8000/admin/`), вы сможете добавлять, редактировать и удалять записи о книгах.

## Заключение

В этом уроке мы создали модель для хранения информации о книгах, применили миграции и научились работать с моделями через Django Shell. В следующих уроках мы углубимся в создание представлений и шаблонов для отображения данных пользователю.

