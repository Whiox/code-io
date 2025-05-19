# code_io

![Pylint](https://github.com/Whiox/code-io/actions/workflows/pylint.yml/badge.svg)
[![Coverage](https://codecov.io/gh/Whiox/code-io/branch/main/graph/badge.svg?token=${{ secrets.CODECOV_TOKEN }} "Codecov report")](https://codecov.io/gh/Whiox/code-io)

## Наш сайт https://code-io.ru/

### Поставлена задача разработать сайт с созданием онлайн курсов

Каждый пользователь может создать неограниченное количество курсов и прочитать любой курс


Курс представляет собой группу файлов формата markdown (.md), разделённых по директориям курса и имеющим свой уникальный id
Для курса можно выбрать его темы, которые будут отображаться на его карточке


На сайте имеется система прогресс внутри курса


Для курсов есть редактор: автор, администратор и staff могут редактировать содержимое курса


Для модерирования курсов, жалоб и других элементов сайта имеется панель модератора, доступ к которой есть у модераторов и staff

### Как мы это сделали?

Мы решили хранить содержимое курсов в markdown файлах (.md, такие же, как и на превью в гите)

Почему мы храним их именно так?
Оптимизация и удобство, .md файлы поддерживают создания заголовков и других HTML прелестей.
Серверу не надо искать в файле большой объём информации, почти всё уже есть в нём


### Запуск

Стандартный

Для работы сайта через питоновский запуск нужно выключить Debug режим

```shell
python manage.py migrate
python manage.py runserver
```

Для запуска через Docker (PortgreSQL, nginx, gunicorn):
```bash
docker-compose up --build
```

### pylint

~~Запускается в CI~~

Для ручного запуска:

```bash
pylint --load-plugins pylint_django --django-settings-module=code_io.settings --fail-under=8 .
```

### Тестирование

~~Выгружается в gitlab artifact после каждого коммита~~

Для тестирования вручную:
```bash
coverage run --rcfile=.coveragerc --source='.' manage.py test
coverage html
```

### Документация

~~Выгружается в gitlab artifact после каждого коммита~~

Для сборки документации вручную:
```bash
cd docs
./make.bat html
```
