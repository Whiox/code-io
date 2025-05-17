Поднятие стека командой


docker-compose up --build
--build — пересобирает образы.

Контейнеры будут доступны по http://localhost:8000.

Логи и отладка

docker-compose logs -f web — смотреть логи Django.

docker-compose exec web bash — зайти внутрь контейнера для запуска команд (migrate, createsuperuser).