"""education views"""

import os
import re
import shutil
import time

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, OuterRef, Exists
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from django.views import View
from django.http import JsonResponse, QueryDict
from django.conf import settings

from code_io.mixins import LoggingMixin

from education.methods import get_most_popular_courses
from education.files import get_all_lessons, get_lesson_number
from education.models import Courses, Lessons, Stars, ReportCourse, Topic, CourseProgress
from education.forms import AddCourseForm, AddLessonForm, TopicChoiceForm


def author_or_staff(user, course):
    """
    Проверяет, является ли пользователь автором курса или имеет права staff.

    :param user: Пользователь Django
    :param course: Экземпляр модели Courses
    :return: True, если пользователь — staff или автор курса, иначе False
    :rtype: bool
    """
    return user.is_staff or course.author == user


class ViewCourseView(LoggingMixin, View):
    """Просмотр содержимого курса."""

    @staticmethod
    def get(request, course_id):
        """
        Отображает страницу курса с перечнем и содержимым уроков.

        :param request: HTTP-запрос Django
        :param int course_id: Идентификатор курса
        :return: render в 'course.html' с контекстом уроков или 'error.html'
        """
        course = get_object_or_404(Courses, course_id=course_id)
        course_path = os.path.join(settings.MEDIA_ROOT, str(course_id))
        if not os.path.exists(course_path):
            return render(request, 'error.html', {'error': 'Курс не найден.'})

        lessons = sorted(os.listdir(course_path), key=get_lesson_number)
        content = get_all_lessons(course, course_path, lessons, [])
        content['course_id'] = course_id
        return render(request, 'course.html', content)


class AllCoursesView(LoggingMixin, View):
    """Просмотр всех курсов с количеством уроков и отметками звезд."""

    @staticmethod
    def get(request):
        """
        Формирует список всех курсов.

        Отмечает, какие курсы пользователь уже «застарил».

        :param request: HTTP-запрос Django
        :return: render в 'all_courses.html' с контекстом курсов
        """
        q = request.GET.get('q', '').strip()
        filter_by = request.GET.get('filter_by', 'title')

        qs = Courses.objects.annotate(
            lessons_count=Count('lessons')
        ).select_related('author').prefetch_related('topics')

        if q:
            if filter_by == 'title':
                qs = qs.filter(title__icontains=q)
            elif filter_by == 'author':
                qs = qs.filter(author__username__icontains=q)
            elif filter_by == 'tags':
                qs = qs.filter(topics__name__icontains=q)
        qs = qs.distinct()

        courses = []
        for course in qs:
            courses.append({
                'id': course.course_id,
                'title': course.title,
                'author': course.author.username if course.author else '—',
                'topics': [t.name for t in course.topics.all()] or ['—'],
                'is_stared': (
                        request.user.is_authenticated
                        and Stars.objects.filter(user=request.user, course=course).exists()
                ),
                'lessons_count': course.lessons_count,
            })

        context = {
            'courses': courses,
            'search': {
                'q': q,
                'filter_by': filter_by,
            }
        }
        return render(request, 'all_courses.html', context)


class StaredCoursesView(LoggingMixin, View):
    """Просмотр курсов, отмеченных звездой текущим пользователем."""

    @staticmethod
    def get(request):
        """
        Отображает страницу со списком «застаренных» курсов.

        :param request: HTTP-запрос Django
        :return: redirect на '/login' если не авторизован, иначе render в 'stared_courses.html'
        """
        if request.user.is_anonymous:
            return redirect('/login')

        stared_ids = Stars.objects.filter(user=request.user).values_list('course_id', flat=True)
        stared_qs = Courses.objects.filter(course_id__in=stared_ids).annotate(
            lessons_count=Count('lessons')
        ).select_related('author').prefetch_related('topics')

        courses = []
        for course in stared_qs:
            topics = [t.name for t in course.topics.all()] or ['Свободная тема']
            courses.append({
                'id': course.course_id,
                'title': course.title,
                'author': course.author.username if course.author else 'Неизвестный автор',
                'topics': topics,
                'is_stared': True,
                'lessons_count': course.lessons_count,
            })

        popular_courses = None
        if not courses:
            popular_courses = get_most_popular_courses(request.user)

        return render(request, 'stared_courses.html', {
            'courses': courses,
            'popular_courses': popular_courses
        })


class MyCoursesView(LoggingMixin, View):
    """Просмотр курсов текущего пользователя."""

    @staticmethod
    def get(request):
        """
        Отображает список курсов, созданных текущим пользователем.

        :param request: HTTP-запрос Django
        :return: redirect на 'login' если не авторизован, иначе render в 'my_courses.html'
        """
        if not request.user.is_authenticated:
            return redirect('login')

        courses = Courses.objects.filter(author=request.user)
        content = {'courses': []}
        for course in courses:
            content['courses'].append({
                'id': course.course_id,
                'title': course.title,
            })
        return render(request, 'my_courses.html', content)


class AdminCoursesView(LoggingMixin, View):
    """Просмотр всех курсов для администраторов."""

    @staticmethod
    def get(request):
        """
        Отображает список всех курсов.

        :param request: HTTP-запрос Django
        :return: redirect на 'login' если не авторизован, иначе render в 'user_courses.html'
        """
        if not request.user.is_authenticated:
            return redirect('login')

        courses = Courses.objects.filter()
        content = {'courses': []}
        for course in courses:
            content['courses'].append({
                'id': course.course_id,
                'title': course.title,
                'author': course.author
            })
        return render(request, 'user_courses.html', content)


class AddCourseView(LoggingMixin, View):
    """Добавление нового курса вместе с уроками и темами."""

    @staticmethod
    def get(request):
        """
        Показывает форму создания курса.

        :param request: HTTP-запрос Django
        :return: render в 'add_course.html' с формами course_form, lesson_formset, topic_form
        """
        if request.user.is_anonymous:
            return redirect('/login')

        LessonFormSet = formset_factory(AddLessonForm, extra=1)
        course_form = AddCourseForm()
        lesson_formset = LessonFormSet()
        topic_form = TopicChoiceForm()
        return render(request, 'add_course.html', {
            'course_form': course_form,
            'lesson_formset': lesson_formset,
            'topic_form': topic_form,
        })

    @staticmethod
    def post(request):
        """
        Обрабатывает отправку формы и сохраняет курс, уроки и файлы.

        :param request: HTTP-запрос Django с POST/FILES
        :return: redirect на 'my_courses' при успехе, иначе render с формами и ошибками
        """
        if request.user.is_anonymous:
            return redirect('/login')

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

            lesson_ids = []
            for idx, lf in enumerate(lesson_formset):
                desc = lf.cleaned_data.get('lesson_description')
                if desc:
                    lesson = Lessons.objects.create(
                        course=course,
                        title=desc,
                        order=idx
                    )
                    lesson_ids.append((lesson.lesson_id, idx))

            folder = os.path.join(settings.MEDIA_ROOT, str(course.course_id))
            os.makedirs(os.path.join(folder, 'tasks'), exist_ok=True)

            for (lesson_pk, idx), lf in zip(lesson_ids, lesson_formset):
                uploaded = lf.cleaned_data.get('lesson_file')
                if uploaded:
                    filename = f"lesson_{idx}.md"
                    path = os.path.join(folder, filename)
                    with open(path, 'wb+') as dst:
                        for chunk in uploaded.chunks():
                            dst.write(chunk)

            return redirect('my_courses')

        return render(request, 'add_course.html', {
            'course_form': course_form,
            'lesson_formset': lesson_formset,
            'topic_form': topic_form,
        })


class DeleteCourseView(LoggingMixin, View):
    """Удаление курса с подтверждением."""

    @staticmethod
    def get(request, course_id):
        """
        Показывает страницу подтверждения удаления курса.

        :param request: HTTP-запрос Django
        :param int course_id: Идентификатор удаляемого курса
        :return: render в 'confirm_delete.html' или 'error.html'
        """
        course = get_object_or_404(Courses, pk=course_id)
        if request.user != course.author:
            return render(request, 'error.html', {'error': 'Вы не автор курса.'})
        return render(request, 'confirm_delete.html', {'course': course})

    @staticmethod
    def post(request, course_id):
        """
        Выполняет удаление курса и его файлов.

        :param request: HTTP-запрос Django
        :param int course_id: Идентификатор удаляемого курса
        :return: redirect на 'my_courses'
        """
        course = get_object_or_404(Courses, pk=course_id)
        if request.user != course.author:
            return render(request, 'error.html', {'error': 'Вы не автор курса.'})

        course_folder = os.path.join(settings.MEDIA_ROOT, str(course.course_id))
        course.delete()
        if os.path.exists(course_folder):
            shutil.rmtree(course_folder)

        return redirect('my_courses')


class AddStar(LoggingMixin, View):
    """Добавление или удаление «звезды» курса через AJAX."""

    @staticmethod
    def post(request, course_id):
        """
        Переключает состояние «звезды» для курса.

        :param request: HTTP-запрос Django (AJAX)
        :param int course_id: Идентификатор курса
        :return: JsonResponse со статусом в ключе "status"
        :rtype: JsonResponse
        """
        if request.user.is_anonymous:
            return JsonResponse({"status": False})

        course = Courses.objects.get(course_id=course_id)
        existing = Stars.objects.filter(user=request.user, course=course).first()
        if existing:
            existing.delete()
            status = False
        else:
            Stars.objects.create(user=request.user, course=course, data=time.time())
            status = True

        return JsonResponse({"status": status})


class LessonProgress(LoggingMixin, View):
    @method_decorator(login_required)
    def get(self, request, course_id, lesson_id):
        lesson = get_object_or_404(Lessons, pk=lesson_id)
        progress, _ = CourseProgress.objects.get_or_create(user=request.user, lesson=lesson)

        return JsonResponse({"status": "ok", "data": progress.status})

    @method_decorator(login_required)
    def post(self, request, course_id, lesson_id):
        lesson = get_object_or_404(Lessons, pk=lesson_id)
        progress, _ = CourseProgress.objects.get_or_create(user=request.user, lesson=lesson)
        progress.status = not progress.status
        progress.save()
        return JsonResponse({"status": "ok", "data": progress.status})


class CourseProgressList(LoggingMixin, View):
    @method_decorator(login_required)
    def get(self, request, course_id):
        progresses = CourseProgress.objects.filter(
            user=request.user,
            lesson__course_id=course_id
        )
        done = [p.lesson_id for p in progresses if p.status]
        return JsonResponse({"status": "ok", "done_lessons": done})


class CourseEditorView(LoggingMixin, View):
    """Редактирование содержимого уроков курса."""

    @method_decorator(login_required)
    def get(self, request, course_id):
        """
        Отображает форму редактора для markdown-файла урока.

        Доступен только автору курса или staff.

        :param request: HTTP-запрос Django
        :param int course_id: Идентификатор курса
        :return: render в 'edit_course.html' с контекстом файлов и содержимого
        """
        course = get_object_or_404(Courses, course_id=course_id)
        if not author_or_staff(request.user, course):
            messages.error(request, "Нет прав на редактирование.")
            return redirect('course', course_id=course_id)

        lessons_qs = Lessons.objects.filter(course=course).order_by('order')
        lessons = [
            {
                'order': les.order,
                'title': les.title,
                'filename': f"lesson_{les.order}.md"
            }
            for les in lessons_qs
        ]

        selected = request.GET.get('lesson', '')
        raw_content = ''
        if selected.isdigit():
            filename = f"lesson_{selected}.md"
            path = os.path.join(settings.MEDIA_ROOT, str(course_id), filename)
            if os.path.isfile(path):
                with open(path, 'r', encoding='utf-8') as fp:
                    raw_content = fp.read()
            else:
                messages.error(request, "Файл урока не найден.")

        all_topics = list(Topic.objects.values('id', 'name'))
        course_topics = list(course.topics.all().values('id', 'name'))

        return render(request, 'edit_course.html', {
            'course': course,
            'lessons': lessons,
            'selected': selected,
            'content': raw_content,
            'all_topics': all_topics,
            'course_topics': course_topics
        })

    @method_decorator(login_required)
    def post(self, request, course_id):
        """
        Сохраняет изменения в markdown-файле урока.

        :param request: HTTP-запрос Django
        :param int course_id: Идентификator курса
        :return: redirect обратно на редактор с параметром lesson
        """
        course = get_object_or_404(Courses, course_id=course_id)
        if not author_or_staff(request.user, course):
            messages.error(request, "Нет прав на редактирование.")
            return redirect('course', course_id=course_id)

        if 'update_topics' in request.POST:
            try:
                topic_ids = list(set(map(int, request.POST.getlist('topics', []))))
                existing_ids = Topic.objects.filter(id__in=topic_ids).values_list('id', flat=True)
                course.topics.set(existing_ids)
                messages.success(request, 'Тематики курса успешно обновлены')
            except Exception as e:
                messages.error(request, f'Ошибка обновления тем: {e}')
            return redirect('course_edit', course_id=course_id)

        lesson_order = request.POST.get('lesson')
        if not (lesson_order and lesson_order.isdigit()):
            messages.error(request, "Урок не выбран или некорректен.")
            return redirect('course_edit', course_id=course_id)

        filename = f"lesson_{lesson_order}.md"
        file_path = os.path.join(settings.MEDIA_ROOT, str(course_id), filename)
        if not os.path.isfile(file_path):
            messages.error(request, "Файл урока не найден.")
            return redirect(f"{request.path}?lesson={lesson_order}")

        new_content = request.POST.get('content', '')
        try:
            with open(file_path, 'wb') as fp:
                fp.write(new_content.encode('utf-8'))
            messages.success(request, f"Урок «{filename}» сохранён.")
        except Exception as e:
            messages.error(request, f"Ошибка при сохранении: {e}")

        return redirect(f"{request.path}?lesson={lesson_order}")


class ReportCourseView(LoggingMixin, View):
    """Обработка жалоб на курс.

    :cvar get: Показать страницу создания или просмотра жалобы.
    :cvar post: Создать новую жалобу.
    :cvar put: Обновить существующую жалобу.
    :cvar delete: Удалить жалобу.
    """

    @method_decorator(login_required)
    def get(self, request, course_id):
        """
        Отображает страницу подачи или просмотра жалобы на курс.

        :param request: HTTP-запрос Django
        :param int course_id: Идентификатор курса
        :return: render 'report_course.html' с контекстом:
                 - course: объект Courses
                 - report (опционально): QuerySet с жалобой пользователя
        :rtype: HttpResponse
        """
        course = get_object_or_404(Courses, course_id=course_id)
        context = {'course': course}

        report = ReportCourse.objects.filter(course=course, author=request.user)
        if report.exists():
            context['report'] = report

        return render(request, 'report_course.html', context)

    @method_decorator(login_required)
    def post(self, request, course_id):
        """
        Создает новую жалобу на курс, если её еще не было.

        :param request: HTTP-запрос Django
        :param int course_id: Идентификатор курса
        :return: JsonResponse со статусом 'ok' и id новой жалобы,
                 или 'error' и описанием ошибки
        :rtype: JsonResponse
        """
        course = get_object_or_404(Courses, course_id=course_id)

        if ReportCourse.objects.filter(course=course, author=request.user).exists():
            return JsonResponse({'status': 'error', 'error': 'report already exists'})

        reason = request.POST.get('reason')
        if not reason:
            return JsonResponse({'status': 'error', 'error': 'no reason field'})

        report = ReportCourse.objects.create(course=course, author=request.user, reason=reason)
        return JsonResponse({'status': 'ok', 'ok': report.id})

    @method_decorator(login_required)
    def put(self, request, course_id):
        """
        Обновляет причину существующей жалобы на курс.

        :param request: HTTP-запрос Django
        :param int course_id: Идентификатор курса
        :return: JsonResponse со статусом 'ok' и id обновленной жалобы,
                 или 'error' и описанием ошибки
        :rtype: JsonResponse
        """
        course = get_object_or_404(Courses, course_id=course_id)

        data = QueryDict(request.body.decode('utf-8'))
        reason = data.get('reason')
        if not reason:
            return JsonResponse({'status': 'error', 'error': 'no reason field'})

        report = ReportCourse.objects.filter(course=course, author=request.user).first()
        if not report:
            return JsonResponse({'status': 'error', 'error': 'report does not exist'})

        report.reason = reason
        report.save()
        return JsonResponse({'status': 'ok', 'ok': report.id})

    @method_decorator(login_required)
    def delete(self, request, course_id):
        """
        Удаляет жалобу пользователя на курс.

        :param request: HTTP-запрос Django
        :param int course_id: Идентификатор курса
        :return: JsonResponse со статусом 'ok' после удаления
        :rtype: JsonResponse
        """
        course = get_object_or_404(Courses, course_id=course_id)
        ReportCourse.objects.filter(course=course, author=request.user).delete()
        return JsonResponse({'status': 'ok', 'ok': 'report deleted'})


class CreateTopicView(LoggingMixin, View):
    @method_decorator(login_required)
    def post(self, request):
        name = request.POST.get('name')

        if not name:
            return JsonResponse({'status': 'error', 'error': 'no name field'})

        if Topic.objects.filter(name=name).exists():
            return JsonResponse({'status': 'error', 'error': 'topic with this name already exist'})

        topic = Topic.objects.create(name=name, author=request.user)

        return JsonResponse({'status': 'ok', 'ok': topic.id})


class GetTopicsView(LoggingMixin, View):
    @method_decorator(login_required)
    def get(self, request):
        qs = Topic.objects.order_by('name').values('id', 'name')

        return JsonResponse({'status': 'ok', 'topics': list(qs)})


class GetTopicView(LoggingMixin, View):
    @method_decorator(login_required)
    def get(self, request, topic_id):
        topic = Topic.objects.filter(id=topic_id).first()

        return JsonResponse({'status': 'ok', 'topic': topic})
