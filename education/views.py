from django.shortcuts import render
import os
import markdown
from education.models import Courses, Lessons, Task
import re
def view_course(request, token):
    course_path = os.path.join('courses', token)
    if not os.path.exists(course_path):
        return render(request, '404.html', {'error': 'Курс не найден.'})

    lessons = os.listdir(course_path)
    lessons_content = []

    def extract_lesson_number(lesson_name):
        match = re.search(r'(\d+)', lesson_name)
        return int(match.group(1)) if match else float('inf')  # Если нет номера, ставим в конец

    lessons.sort(key=extract_lesson_number)

    for index, lesson in enumerate(lessons):
        lesson_path = os.path.join(course_path, lesson)

        if os.path.isfile(lesson_path):
            try:
                with open(lesson_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                    html_content = markdown.markdown(
                        md_content,
                        extensions=[
                            'fenced_code',  # Для поддержки fenced code blocks
                            'codehilite',   # Для выделения кода
                            'tables',       # Если у вас есть таблицы
                        ]
                    )
                    lesson_title = f"Урок {index + 1}"
                    lessons_content.append({'title': lesson_title, 'content': html_content})
            except Exception as e:
                print(f"Ошибка при чтении файла {lesson}: {e}")
                lesson_title = f"Урок {index + 1}"
                lessons_content.append({'title': lesson_title, 'content': f"<p>Ошибка при загрузке урока: {lesson}</p>"})
        else:
            lesson_title = f"Урок {index + 1}"
            lessons_content.append({'title': lesson_title, 'content': "<p>Урок пуст.</p>"})

    return render(request, 'course.html', {'lessons': lessons_content})





def all_courses(request):
    courses = Courses.objects.all()
    content = {
        'courses': []
    }
    for course in courses:
        course_info = {
            'id': course.course_id,
            'title': course.title
        }
        content['courses'].append(course_info)

    print(content['courses'])

    return render(request, 'all_courses.html', content)

