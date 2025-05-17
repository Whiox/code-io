`Базовый Dockerfile

```
# 1. Выбираем базовый образ
FROM python:3.11-slim

# 2. Создаём рабочую директорию
WORKDIR /app

# 3. Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Копируем исходники
COPY . .

# 5. Выполняем сборку статических файлов (если нужно)
# RUN python manage.py collectstatic --noinput

# 6. Открываем порт приложения
EXPOSE 8000

# 7. Стандартная команда запуска
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
```
