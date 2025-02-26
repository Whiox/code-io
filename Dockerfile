FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN python manage.py collectstatic --no-input --clear

CMD ["gunicorn", "code_io.wsgi:application", "--bind", "0.0.0.0:8000"]
