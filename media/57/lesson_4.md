5.1. Настройка окружений GitHub
Environments: staging и production.

В каждом окружении можно настроить защиту (reviews) и секреты (например, SSH‑ключи).

5.2. Деплой по push‑webhook (SSH)
###Добавим следующий job:

```
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
      - uses: actions/checkout@v3

      - name: Install SSH key
        uses: webfactory/ssh-agent@v0.8.1
        with:
          ssh-private-key: ${{ secrets.DEPLOY_SSH_KEY }}

      - name: Deploy to server
        run: |
          ssh user@your.server.com "
            docker pull ${{ secrets.DOCKERHUB_USER }}/myproject:${{ github.sha }} &&
            docker stop myproject || true &&
            docker rm myproject || true &&
            docker run -d \
              --name myproject \
              -e DATABASE_URL=${{ secrets.PROD_DATABASE_URL }} \
              -p 8000:8000 \
              ${{ secrets.DOCKERHUB_USER }}/myproject:${{ github.sha }}
          "
```

### Пояснения
if: github.ref == 'refs/heads/main' — деплой только из main.

environment: production — позволяет привязывать approvals и секреты.

SSH‑ключ в секрете DEPLOY_SSH_KEY: приватный ключ для доступа к серверу.

На сервере Docker должен быть установлен и запущен демон.