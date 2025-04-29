import os
from .chain import lesson_chain

def get_all_lessons(course, course_path, lessons, lessons_content):
    """
    course_path — абсолютный путь к папке с MD-файлами (директория курса)
    lessons — список имён файлов (.md), уже отсортированных
    lessons_content — пустой список, в который будем добавлять результаты
    """
    for lesson_name in lessons:
        lesson_path = os.path.join(course_path, lesson_name)
        if os.path.isfile(lesson_path):
            try:
                # прокидываем в цепочку (path, filename, course_path)
                lesson_data = lesson_chain.handle((lesson_path, lesson_name, course_path))
                lessons_content.append(lesson_data)
            except Exception as e:
                lessons_content.append({
                    'title': f"Урок {lesson_name}",
                    'content': f"<p>Ошибка при загрузке урока: {e}</p>",
                    'tasks': [],
                })
        else:
            lessons_content.append({
                'title': f"Урок {lesson_name}",
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
