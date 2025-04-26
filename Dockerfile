# --- Единственная стадия, без компиляции psycopg2 ---
FROM python:3.11-alpine
WORKDIR /app

# только рантайм-зависимости
RUN apk add --no-cache postgresql-libs

# копируем всё и ставим питон-пакеты
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# собираем статику на старте
CMD ["sh", "-c", \
     "python manage.py collectstatic --no-input && ", \
     "gunicorn code_io.wsgi:application --bind 0.0.0.0:8000 --workers 3"]
