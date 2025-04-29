import os
import re
import markdown
from education.methods import get_metadata

class Handler:
    def __init__(self, nxt=None):
        self.nxt = nxt

    def handle(self, data):
        ctx = self.process(data)
        if self.nxt:
            return self.nxt.handle(ctx)
        return ctx

    def process(self, data):
        raise NotImplementedError


class ReadFileHandler(Handler):
    """
    Читает содержимое файла.
    data = (lesson_path, lesson_name, course_path)
    возвращает {'raw': ..., 'lesson_name': ..., 'course_path': ...}
    """
    def process(self, data):
        lesson_path, lesson_name, course_path = data
        with open(lesson_path, 'r', encoding='utf-8') as f:
            raw = f.read()
        return {
            'raw': raw,
            'lesson_name': lesson_name,
            'course_path': course_path,
        }


class MetadataHandler(Handler):
    """
    Извлекает метаданные из raw.
    """
    def process(self, ctx):
        meta, body = get_metadata(ctx['raw'])
        ctx.update({
            'meta': meta,
            'body': body,
        })
        return ctx


class MarkdownHandler(Handler):
    """
    Конвертирует оставшийся markdown в HTML.
    """
    def process(self, ctx):
        html = markdown.markdown(
            ctx['body'],
            extensions=['fenced_code', 'codehilite', 'tables']
        )
        ctx['html'] = html
        return ctx


class TaskHandler(Handler):
    """
    Находит и парсит файлы задач для данного урока.
    """
    def process(self, ctx):
        course_path = ctx['course_path']
        lesson_id = re.search(r'(\d+)', ctx['lesson_name']).group(1)
        tasks_dir = os.path.join(course_path, 'tasks')
        tasks = []
        if os.path.isdir(tasks_dir):
            for fn in os.listdir(tasks_dir):
                m = re.match(r'(\d+)_tusk_lesson_(\d+)\.md', fn)
                if m and m.group(2) == lesson_id:
                    with open(os.path.join(tasks_dir, fn), 'r', encoding='utf-8') as f:
                        raw_task = f.read()
                    meta_t, body_t = get_metadata(raw_task)
                    html_t = markdown.markdown(
                        body_t,
                        extensions=['fenced_code', 'codehilite', 'tables']
                    )
                    tasks.append({
                        'task_id': m.group(1),
                        'content': html_t,
                        'right_answer': meta_t.get('right_answer', ''),
                    })
        ctx['tasks'] = tasks
        return ctx


class BuildResultHandler(Handler):
    """
    Собирает итоговую структуру урока.
    """
    def process(self, ctx):
        return {
            'title': ctx['meta'].get('title', f"Урок {ctx['lesson_name']}"),
            'content': ctx['html'],
            'tasks': ctx['tasks'],
        }


lesson_chain = ReadFileHandler(
    MetadataHandler(
        MarkdownHandler(
            TaskHandler(
                BuildResultHandler()
            )
        )
    )
)
