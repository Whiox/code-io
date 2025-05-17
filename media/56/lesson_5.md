Применение миграций

docker-compose exec web python manage.py migrate

Сборка и выдача статических файлов

docker-compose exec web python manage.py collectstatic --noinput
Подключите том для папки static или отдавайте её через Nginx.

```
  nginx:
    image: nginx:stable
    ports:
      - "80:80"
    volumes:
      - ./deploy/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web
```
В nginx.conf пропишите прокси на web:8000, отдачу статики из тома.