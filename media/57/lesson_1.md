###Структура проекта

```
myproject/
├── .github/
│   └── workflows/
│       └── ci.yml
├── manage.py
├── requirements.txt
├── myproject/
│   ├── settings.py
│   └── wsgi.py
└── app1/
    └── models.py
```

###Файл рабочего процесса: .github/workflows/ci.yml

```
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    env:
      DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run migrations
        run: python manage.py migrate --noinput

      - name: Run tests
        run: pytest --maxfail=1 --disable-warnings -q
```

####Пояснения
#####on — триггеры: пуши и PR в ветку main.

#####services: postgres — докер‑сервис для базы.

#####Установка Python и зависимостей — стандартные шаги.

#####Миграции + тесты — сразу проверяем, что всё работает на чистой БД.