import os
import markdown
import re
import shutil
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.forms import formset_factory
from .forms import AddCourseForm, AddLessonForm,TopicChoiceForm
from education.models import Courses, Lessons, Task
from authentication.models import User
from django.conf import settings


def view_course(request, token):
    course = Courses.objects.filter(course_id=token).first()
    course_path = os.path.join('courses', token)
    if not os.path.exists(course_path):
        return render(request, '404.html', {'error': 'Курс не найден.'})

    lessons = os.listdir(course_path)
    lessons_content = []

    def extract_lesson_number(lesson_name):
        match = re.search(r'(\d+)', lesson_name)
        return int(match.group(1)) if match else float('inf')

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
                            'fenced_code',
                            'codehilite',
                            'tables',
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

    return render(request, 'course.html', {'lessons': lessons_content, 'name': course.title})


def all_courses(request):
    courses = Courses.objects.all()
    content = {
        'courses': []
    }
    for course in courses:
        topics = course.topics.all()
        topic_names = [topic.name for topic in topics]
        if not topic_names:
            topic_names = ['Свободная тема']
        course_info = {
            'id': course.course_id,
            'title': course.title,
            'author': course.author.username if course.author else 'Неизвестный автор',
            'topics': topic_names
        }
        content['courses'].append(course_info)

    return render(request, 'all_courses.html', content)

def my_courses(request):
    if not request.user.is_authenticated:
        return redirect('login')
    courses = Courses.objects.filter(author=request.user)
    content = {
        'courses': []
    }
    for course in courses:
        course_info = {
            'id': course.course_id,
            'title': course.title,
        }
        content['courses'].append(course_info)
    return render(request, 'my_courses.html', content)

def add_course(request):
    LessonFormSet = formset_factory(AddLessonForm, extra=1)
    topic_form = TopicChoiceForm()
    if request.method == 'POST':
        course_form = AddCourseForm(request.POST)
        lesson_formset = LessonFormSet(request.POST, request.FILES)
        topic_form = TopicChoiceForm(request.POST)
        if course_form.is_valid() and lesson_formset.is_valid() and topic_form.is_valid():
            course = Courses.objects.create(title=course_form.cleaned_data['course_name'], author=request.user)
            selected_topics = topic_form.cleaned_data['topics']
            course.topics.set(selected_topics)
            lesson_ids = []
            for lesson_form in lesson_formset:
                if lesson_form.cleaned_data and lesson_form.cleaned_data.get('lesson_description'):
                    lesson_title = lesson_form.cleaned_data['lesson_description']
                    lesson = Lessons.objects.create(course=course, title=lesson_title)
                    lesson_ids.append(lesson.lesson_id)

            course_folder = os.path.join(settings.MEDIA_ROOT, str(course.course_id))
            os.makedirs(course_folder, exist_ok=True)

            for lesson_form, lesson_id in zip(lesson_formset, lesson_ids):
                lesson_file = lesson_form.cleaned_data.get('lesson_file')
                if lesson_file:
                    new_file_name = f"lesson_{lesson_id}{os.path.splitext(lesson_file.name)[1]}"
                    file_path = os.path.join(course_folder, new_file_name)
                    with open(file_path, 'wb+') as destination:
                        for chunk in lesson_file.chunks():
                            destination.write(chunk)

            return redirect('my_courses')
    else:
        course_form = AddCourseForm()
        lesson_formset = LessonFormSet()

    return render(request, 'add_course.html', {
        'course_form': course_form,
        'lesson_formset': lesson_formset,
        'topic_form': topic_form,
    })

def delete_course(request, course_id):
    course = get_object_or_404(Courses, pk=course_id)
    if request.method == 'POST':
        course_folder = os.path.join(settings.MEDIA_ROOT, str(course.course_id))
        course.delete()
        if os.path.exists(course_folder):
            shutil.rmtree(course_folder)
        return redirect('my_courses')
    return render(request, 'confirm_delete.html', {'course': course})