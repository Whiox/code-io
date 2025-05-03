FROM python:3.11-alpine
WORKDIR /app

RUN apk add --no-cache postgresql-libs

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", \
     "python manage.py collectstatic --no-input && ", \
     "gunicorn code_io.wsgi:application --bind 0.0.0.0:8000 --workers 3"]
