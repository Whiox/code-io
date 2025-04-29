import os
import re
import shutil
import time

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from django.views import View
from django.http import JsonResponse
from django.conf import settings

from education.files import get_all_lessons, get_lesson_number
from education.models import Courses, Lessons, Stars
from education.forms import AddCourseForm, AddLessonForm, TopicChoiceForm


def author_or_staff(user, course):
    return user.is_staff or course.author == user


class ViewCourseView(View):
    @staticmethod
    def get(request, course_id):
        """
        Отображает курс по его id.

        :param request: HTTP Django request
        :param course_id: Уникальный идентификатор курса
        :return: render: course.html с содержимым уроков
        """
        course = get_object_or_404(Courses, course_id=course_id)
        course_path = os.path.join(settings.MEDIA_ROOT, str(course_id))
        if not os.path.exists(course_path):
            return render(request, 'error.html', {'error': 'Курс не найден.'})

        lessons = sorted(os.listdir(course_path), key=get_lesson_number)
        content = get_all_lessons(course, course_path, lessons, [])
        content['course_id'] = course_id
        return render(request, 'course.html', content)


class AllCoursesView(View):
    @staticmethod
    def get(request):
        """
        Отображает все доступные курсы с количеством уроков и отметкой 'is_stared'.
        """
        courses_qs = Courses.objects.annotate(
            lessons_count=Count('lessons')  # подпишем количество уроков
        ).select_related('author').prefetch_related('topics')

        content = {'courses': []}
        for course in courses_qs:
            topics = [t.name for t in course.topics.all()] or ['Свободная тема']
            is_stared = False
            if request.user.is_authenticated:
                is_stared = Stars.objects.filter(user=request.user, course=course).exists()

            content['courses'].append({
                'id': course.course_id,
                'title': course.title,
                'author': course.author.username if course.author else 'Неизвестный автор',
                'topics': topics,
                'is_stared': is_stared,
                'lessons_count': course.lessons_count,
            })

        return render(request, 'all_courses.html', content)


class StaredCoursesView(View):
    @staticmethod
    def get(request):
        """
        Отображает курсы, на которые пользователь поставил звёздочку,
        с прогрессом (количеством уроков).
        """
        if request.user.is_anonymous:
            return redirect('/login')

        stared_ids = Stars.objects.filter(
            user=request.user
        ).values_list('course_id', flat=True)

        stared_qs = Courses.objects.filter(
            course_id__in=stared_ids
        ).annotate(
            lessons_count=Count('lessons')
        ).select_related('author').prefetch_related('topics')

        content = {
            'courses': []
        }
        for course in stared_qs:
            topics = [t.name for t in course.topics.all()] or ['Свободная тема']
            content['courses'].append({
                'id': course.course_id,
                'title': course.title,
                'author': course.author.username if course.author else 'Неизвестный автор',
                'topics': topics,
                'is_stared': True,
                'lessons_count': course.lessons_count,
            })

        return render(request, 'stared_courses.html', content)


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
        """
        Сохранение файла
        """
        LessonFormSet = formset_factory(AddLessonForm, extra=1)
        course_form = AddCourseForm(request.POST)
        lesson_formset = LessonFormSet(request.POST, request.FILES)
        topic_form = TopicChoiceForm(request.POST)

        if course_form.is_valid() and lesson_formset.is_valid() and topic_form.is_valid():
            course = Courses.objects.create(
                title=course_form.cleaned_data['course_name'],
                author=request.user
            )
            course.topics.set(topic_form.cleaned_data['topics'])

            # создаём уроки в БД
            lesson_ids = []
            for lf in lesson_formset:
                desc = lf.cleaned_data.get('lesson_description')
                if desc:
                    lesson = Lessons.objects.create(course=course, title=desc)
                    lesson_ids.append(lesson.lesson_id)

            # сохраняем файлы
            folder = os.path.join(settings.MEDIA_ROOT, str(course.course_id))
            os.makedirs(folder, exist_ok=True)
            os.makedirs(os.path.join(folder, 'tasks'), exist_ok=True)
            for lf, lid in zip(lesson_formset, lesson_ids):
                uploaded = lf.cleaned_data.get('lesson_file')
                if uploaded:
                    ext = os.path.splitext(uploaded.name)[1]
                    name = f"lesson_{lid}{ext}"
                    path = os.path.join(folder, name)
                    with open(path, 'wb+') as dst:
                        for chunk in uploaded.chunks():
                            dst.write(chunk)

            return redirect('my_courses')

        return render(request, 'add_course.html', {
            'course_form': course_form,
            'lesson_formset': lesson_formset,
            'topic_form': topic_form,
        })


class DeleteCourseView(View):
    @staticmethod
    def get(request, course_id):
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

    @staticmethod
    def post(request, course_id):
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
        if request.user.is_anonymous:
            return JsonResponse({"status": False})

        course = Courses.objects.get(course_id=course_id)
        is_stared = Stars.objects.filter(user=request.user, course=course).first()

        if is_stared:
            is_stared.delete()
            status = False
        else:
            Stars.objects.create(user=request.user, course=course, data=time.time())
            status = True

        return JsonResponse({"status": status})


class CourseEditorView(View):
    """
    Показывает список файлов-уроков курса и позволяет править выбранный файл.
    Править могут только автор курса или staff-пользователь.
    """

    @method_decorator(login_required)
    def get(self, request, course_id):
        course = get_object_or_404(Courses, course_id=course_id)
        if not author_or_staff(request.user, course):
            messages.error(request, "Нет прав на редактирование.")
            return redirect('course', course_id=course_id)

        course_dir = os.path.join(settings.MEDIA_ROOT, str(course_id))
        try:
            files = sorted(
                [f for f in os.listdir(course_dir) if f.endswith('.md')],
                key=lambda fn: int(re.search(r'(\d+)', fn).group(1))
            )
        except FileNotFoundError:
            messages.error(request, "Каталог не найден.")
            return redirect('course', course_id=course_id)

        sel = request.GET.get('lesson')
        raw_content = ''
        if sel in files:
            # читаем через цепочку только raw, без конвертации
            path = os.path.join(course_dir, sel)
            with open(path, encoding='utf-8') as fp:
                raw_content = fp.read()

        return render(request, 'edit_course.html', {
            'course': course,
            'files': files,
            'selected': sel,
            'content': raw_content,
        })

    @method_decorator(login_required)
    def post(self, request, course_id):
        course = get_object_or_404(Courses, course_id=course_id)
        if not author_or_staff(request.user, course):
            messages.error(request, "Нет прав на редактирование.")
            return redirect('course', course_id=course_id)

        lesson = request.POST.get('lesson')
        new_content = request.POST.get('content', '')
        course_dir = os.path.join(settings.MEDIA_ROOT, str(course_id))
        file_path = os.path.join(course_dir, lesson or '')
        if not lesson or not os.path.isfile(file_path):
            messages.error(request, "Некорректный урок.")
            return redirect('course_edit', course_id=course_id)

        try:
            with open(file_path, 'w', encoding='utf-8') as fp:
                fp.write(new_content)
            messages.success(request, f"Урок «{lesson}» сохранён.")
        except Exception as e:
            messages.error(request, f"Ошибка при сохранении: {e}")

        return redirect(f"{request.path}?lesson={lesson}")
