# Проект первой команды

# code_io

### Поставлена задача разработать сайт с созданием онлайн курсов
Каждый пользователь может создать курс

Каждый пользователь может прочитать любой курс

### Запуск

Стандартный

```shell
python manage.py migrate
python manage.py runserver
```

Для запуска через Docker (PortgreSQL, nginx, gunicorn):
```bash
docker-compose up --build
```

### Тестирование

Выгружается в gitlab artifact после каждого коммита

Для тестирования вручную:
```bash
coverage run --source='.' manage.py test
coverage html
```

### Документация

Выгружается в gitlab artifact после каждого коммита

Для сборки документации вручную:
```bash
cd docs
./make.bat html
```
