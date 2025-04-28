import os
import markdown
import re
import shutil
import time

from django.db.models import Count

from education.files import get_all_lessons, get_lesson_number
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.forms import formset_factory
from education.forms import AddCourseForm, AddLessonForm,TopicChoiceForm
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

        lessons.sort(key=get_lesson_number)

        content = get_all_lessons(course, course_path, lessons, lessons_content)
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
            os.makedirs(course_folder + "/tasks", exist_ok=True)
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
