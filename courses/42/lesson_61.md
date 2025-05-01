# course_2025

## Ссылка на Docker-репозиторий https://hub.docker.com/repositories/whiox

# Запуск сервера

## Через python

```shell

git clone https://gitlab.informatics.ru/devops_pro/course_2025.git

cd course_2025

git checkout users/mologin_f/master

pip install -r requirements

python main.py

````

## Локальная сборка

```bash

git clone https://gitlab.informatics.ru/devops_pro/course_2025.git

cd course_2025

git checkout users/mologin_f/master

./docker_multiarch_build.sh

```

### amd64

```bash

docker run -p 5000:5000 whiox/trafficlight-flask:v0.1-amd64

```

### arm64

```bash

docker run -p 5000:5000 whiox/trafficlight-flask:v0.1-arm64

```

## Через опубликованный образ

### amd64

```bash

docker pull whiox/trafficlight-flask:v0.1-amd64

docker run -p 5000:5000 whiox/trafficlight-flask:v0.1-amd64

```

### arm64

```bash

docker pull whiox/trafficlight-flask:v0.1-arm64

docker run -p 5000:5000 whiox/trafficlight-flask:v0.1-arm64

```

## Через кубернетос

```bash

git clone https://gitlab.informatics.ru/devops_pro/course_2025.git

cd course_2025

cd infra

kubectl apply -f ./deployment.yaml

kubectl port-forward svc/devops-server-balancer 5000:5000

```

# Тестировка сервера

## real time

```bash

python main.py

python test/send_request_and_check_response.py

```

## unit

```bash

pytest tests/trafficlights_states.py -v

```

## url

```bash

pytest tests\urls\trafficlight.py -v

```

## image

```bash

pytest tests\trafficlights_images.py -v

```

## static

```bash

mypy main.py

```

