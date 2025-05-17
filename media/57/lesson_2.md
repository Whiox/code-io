###Добавляем линтер и форматтер
flake8 для PEP8‑совместимости и обнаружения ошибок.

black для автоформатирования.

В requirements.txt

```
Django>=4.0
pytest
pytest-django
flake8
black
```

### Расширяем ci.yml
```
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

+     - name: Lint with flake8
+       run: |
+         pip install flake8
+         flake8 .

+     - name: Format check with black
+       run: |
+         pip install black
+         black --check .
      
      - name: Run migrations
```

### Покрытие тестами (coverage)
####Добавьте в requirements.txt:

```
coverage
```
И после тестов:

yaml
```
      - name: Run tests with coverage
        run: |
          pip install coverage
          coverage run -m pytest
          coverage report
```
####Если покрытие падает ниже, скажем, 80%, можно падать сборку:

```
coverage run -m pytest
coverage report --fail-under=80
```