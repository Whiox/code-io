import os
import re
import markdown
from education.methods import get_metadata


def get_all_lessons(course, course_path, lessons, lessons_content):
    for index, lesson in enumerate(lessons):
        lesson_path = os.path.join(course_path, lesson)

        if os.path.isfile(lesson_path):
            try:
                lessons_content.append(get_file_content(lesson_path, lesson, course_path))
            except Exception as e:
                print(f"Ошибка при чтении файла {lesson}: {e}")
                lesson_title = f"Урок {index + 1}"
                lessons_content.append({
                    'title': lesson_title,
                    'content': f"<p>Ошибка при загрузке урока: {lesson}</p>",
                    'tasks': [],
                })
        else:
            lesson_title = f"Урок {index + 1}"
            lessons_content.append({
                'title': lesson_title,
                'content': "<p>Урок пуст.</p>",
                'tasks': [],
            })
    # Удаляем последний урок, если папка tasks найдена
    tasks_path = os.path.join(course_path, 'tasks')
    if os.path.exists(tasks_path):
        if lessons_content:
            lessons_content.pop()
    return {'lessons': lessons_content, 'name': course.title}


def get_file_content(lesson_path, lesson, course_path):
    with open(lesson_path, 'r', encoding='utf-8') as file:
        md_content = file.read()

        html_content = markdown.markdown(
            md_content,
            extensions=[
                'fenced_code',
                'codehilite',
                'tables',
            ]
        )
        lesson_id = re.search(r'(\d+)', lesson).group(1)

        tasks_content = get_task_from_lesson(course_path, lesson_id)

        return {
            'content': html_content,
            'tasks': tasks_content,
        }


def get_task_from_lesson(course_path, lesson_id):
    tasks_path = os.path.join(course_path, 'tasks')
    tasks = os.listdir(tasks_path)
    tasks_content = []
    for task in tasks:
        task_path = os.path.join(tasks_path, task)
        if os.path.isfile(task_path):
            # Извлечение ID урока из имени файла задачи
            task_match = re.match(r'(\d+)_tusk_lesson_(\d+)\.md', task)
            if task_match:
                task_id, task_lesson_id = task_match.groups()

                if task_lesson_id == lesson_id:  # Сравниваем с ID текущего урока
                    with open(task_path, 'r', encoding='utf-8') as f:
                        task_content = f.read()
                        # Извлечение метаданных и контента задачи
                        task_metadata, task_content = get_metadata(task_content)
                        task_html_content = markdown.markdown(
                            task_content,
                            extensions=[
                                'fenced_code',
                                'codehilite',
                                'tables',
                            ]
                        )
                        tasks_content.append({
                            'content': task_html_content,
                            'right_answer': task_metadata.get('right_answer', ''),
                            # Извлечение правильного ответа
                            'task_id': task_id,  # Добавляем ID задачи
                        })
    return tasks_content

def get_lesson_number(lesson_name):
    match = re.search(r'(\d+)', lesson_name)
    return int(match.group(1)) if match else float('inf')
