# Заголовок первого уровня

## Заголовок второго уровня

Это пример простого Markdown файла. 

### Список

- Пункт 1
- Пункт 2
- Пункт 3

### Нумерованный список

1. Первый элемент
2. Второй элемент
3. Третий элемент

### Выделение текста

*Курсив* и **жирный** текст.

### Ссылки и изображения
![Это изображение](https://fresco.wallset.ru/images/detailed/1208/3086.jpg)

### Код

```python
def render_markdown(request):
    md_file_path = os.path.join('md_files', 'example.md')
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    html_content = markdown.markdown(md_content, extensions=['fenced_code', 'codehilite'])
    return render(request, 'render.html', {'content': html_content})
```