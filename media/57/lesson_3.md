###Создание образа в CI
####Добавим стадию build-and-push после успешных тестов:

```
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Log in to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USER }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ secrets.DOCKERHUB_USER }}/myproject:${{ github.sha }}
```

Секреты DOCKERHUB_USER и DOCKERHUB_TOKEN настраиваются в настройках репозитория.

Образ помечается по SHA коммита, чтобы каждому билд‑артефакту соответствовал свой тег.