import os
from .chain import lesson_chain
import re
from education.models import Lessons

def get_all_lessons(course, course_path, lessons, lessons_content):
    """
    course_path — абсолютный путь к папке с MD-файлами (директория курса)
    lessons — список имён файлов (.md), уже отсортированных
    lessons_content — пустой список, в который будем добавлять результаты
    """
    for lesson_name in lessons:
        m = re.match(r'lesson_(\d+)\.md', lesson_name)
        idx = int(m.group(1)) if m else None

        title = None
        if idx is not None:
            try:
                obj = Lessons.objects.get(course=course, order=idx)
                title = obj.title
            except Lessons.DoesNotExist:
                title = None

        lesson_path = os.path.join(course_path, lesson_name)
        if os.path.isfile(lesson_path):
            try:
                data = lesson_chain.handle((lesson_path, lesson_name, course_path))
                if title:
                    data['title'] = title
                lessons_content.append(data)
            except Exception as e:
                lessons_content.append({
                    'title': title or f"Урок {idx}",
                    'content': f"<p>Ошибка при загрузке: {e}</p>",
                    'tasks': [],
                })
        else:
            lessons_content.append({
                'title': title or f"Урок {idx}",
                'content': "<p>Урок пуст.</p>",
                'tasks': [],
            })

    # если есть папка tasks — убрать последний элемент (служебный файл)
    tasks_path = os.path.join(course_path, 'tasks')
    if os.path.exists(tasks_path) and lessons_content:
        lessons_content.pop()

    return {
        'lessons': lessons_content,
        'name': course.title,
    }

def get_lesson_number(lesson_name):
    import re
    m = re.search(r'(\d+)', lesson_name)
    return int(m.group(1)) if m else float('inf')
