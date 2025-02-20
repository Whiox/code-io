import os
import markdown
import re
import shutil
import time
from education.methods import get_metadata
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.forms import formset_factory
from .forms import AddCourseForm, AddLessonForm,TopicChoiceForm
from education.models import Courses, Lessons, Stars
from django.views import View
from django.conf import settings
from django.http import JsonResponse


class ViewCourseView(View):
    @staticmethod
    def get(request, course_id):
        """
        Отображает курс по его id.

        :param request: HTTP Django request
        :param course_id: Уникальный идентификатор курса
        :return: render: course.html с содержимым уроков
        """
        course = Courses.objects.filter(course_id=course_id).first()
        course_path = os.path.join('courses', course_id)
        if not os.path.exists(course_path):
            return render(request, 'error.html', {'error': 'Курс не найден.'})

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
                        # Конвертация основного контента в HTML
                        html_content = markdown.markdown(
                            md_content,
                            extensions=[
                                'fenced_code',
                                'codehilite',
                                'tables',
                            ]
                        )
                        lesson_id = re.search(r'(\d+)', lesson).group(1)  # Извлечение ID урока из имени файла
                        lesson_title = f"Урок {lesson_id}"

                        # Загрузка задач
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

                        lessons_content.append({
                            'content': html_content,
                            'tasks': tasks_content,
                        })
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
        return render(request, 'course.html', {'lessons': lessons_content, 'name': course.title})


class AllCoursesView(View):
    @staticmethod
    def get(request):
        """
        Отображает все доступные курсы.

        :param request: HTTP Django request
        :return: render: all_courses.html со списком курсов
        """
        courses = Courses.objects.all()
        content = {
            'courses': []
        }
        for course in courses:
            topics = course.topics.all()
            topic_names = [topic.name for topic in topics]
            if not topic_names:
                topic_names = ['Свободная тема']
            if request.user.is_authenticated:
                is_stared = Stars.objects.filter(user=request.user, course=course)
            else:
                is_stared = False
            course_info = {
                'id': course.course_id,
                'title': course.title,
                'author': course.author.username if course.author else 'Неизвестный автор',
                'topics': topic_names,
                'is_stared': True if is_stared else False
            }
            content['courses'].append(course_info)

        return render(request, 'all_courses.html', content)


class MyCoursesView(View):
    @staticmethod
    def get(request):
        """
        Отображает курсы, созданные текущим пользователем.

        :param request: HTTP Django request
        :return: render: my_courses.html со списком курсов пользователя
        """
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


class AddCourseView(View):
    @staticmethod
    def get(request):
        LessonFormSet = formset_factory(AddLessonForm, extra=1)
        course_form = AddCourseForm()
        lesson_formset = LessonFormSet()
        topic_form = TopicChoiceForm()

        content = {
            'course_form': course_form,
            'lesson_formset': lesson_formset,
            'topic_form': topic_form,
        }

        return render(request, 'add_course.html', content)

    @staticmethod
    def post(request):
        LessonFormSet = formset_factory(AddLessonForm, extra=1)
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

        content = {
            'course_form': course_form,
            'lesson_formset': lesson_formset,
            'topic_form': topic_form,
        }

        return render(request, 'add_course.html', content)


class DeleteCourseView(View):
    def get(self, request, course_id):
        """
        Возвращает шаблон для подтверждения удаления курса.
        Проверяет, является ли пользователь автором курса.

        :param request: HTTP Django request
        :param course_id: ID курса для удаления
        :return: render: confirm_delete.html или error.html
        """
        course = get_object_or_404(Courses, pk=course_id)
        if request.user != course.author:
            return render(request, 'error.html', {'error': 'Вы не автор курса.'})
        return render(request, 'confirm_delete.html', {'course': course})

    def post(self, request, course_id):
        """
        Обрабатывает POST запрос для удаления курса.
        Удаляет курс из базы данных и его папку из файловой системы.

        :param request: HTTP Django request
        :param course_id: ID курса для удаления
        :return: redirect: my_courses
        """
        course = get_object_or_404(Courses, pk=course_id)
        if request.user != course.author:
            return render(request, 'error.html', {'error': 'Вы не автор курса.'})

        # Удаляем курс и его папку
        course_folder = os.path.join(settings.MEDIA_ROOT, str(course.course_id))
        course.delete()
        if os.path.exists(course_folder):
            shutil.rmtree(course_folder)

        return redirect('my_courses')


class AddStar(View):
    """Логика для постановки звезды на курс"""

    @staticmethod
    def post(request, course_id):
        course = Courses.objects.get(course_id=course_id)
        is_stared = Stars.objects.filter(user=request.user, course=course).first()

        if is_stared:
            is_stared.delete()
            status = False
        else:
            Stars.objects.create(user=request.user, course=course, data=time.time())
            status = True

        return JsonResponse({"status": status})
