"""education views"""

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
from django.http import JsonResponse, QueryDict
from django.conf import settings

from education.files import get_all_lessons, get_lesson_number
from education.models import Courses, Lessons, Stars, ReportCourse, Topic
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


class ViewCourseView(View):
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


class AllCoursesView(View):
    """Просмотр всех курсов с количеством уроков и отметками звезд."""

    @staticmethod
    def get(request):
        """
        Формирует список всех курсов.

        Отмечает, какие курсы пользователь уже «застарил».

        :param request: HTTP-запрос Django
        :return: render в 'all_courses.html' с контекстом курсов
        """
        courses_qs = Courses.objects.annotate(
            lessons_count=Count('lessons')
        ).select_related('author').prefetch_related('topics')

        content = {'courses': []}
        for course in courses_qs:
            topics = [t.name for t in course.topics.all()] or ['Свободная тема']
            is_stared = (
                request.user.is_authenticated and
                Stars.objects.filter(user=request.user, course=course).exists()
            )
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

        stared_ids = Stars.objects.filter(
            user=request.user
        ).values_list('course_id', flat=True)
        stared_qs = Courses.objects.filter(
            course_id__in=stared_ids
        ).annotate(
            lessons_count=Count('lessons')
        ).select_related('author').prefetch_related('topics')

        content = {'courses': []}
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


class AddCourseView(View):
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
            for lf in lesson_formset:
                desc = lf.cleaned_data.get('lesson_description')
                if desc:
                    lesson = Lessons.objects.create(course=course, title=desc)
                    lesson_ids.append(lesson.lesson_id)

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


class AddStar(View):
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


class CourseEditorView(View):
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
            path = os.path.join(course_dir, sel)
            with open(path, encoding='utf-8') as fp:
                raw_content = fp.read()

        all_topics = list(Topic.objects.values('id', 'name'))
        course_topics = list(course.topics.all().values('id', 'name'))

        return render(request, 'edit_course.html', {
            'course': course,
            'files': files,
            'selected': sel,
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
                messages.error(request, f'Ошибка обновления тем: {str(e)}')
            return redirect('course_edit', course_id=course_id)

        lesson = request.POST.get('lesson')
        new_content = request.POST.get('content', '')
        course_dir = os.path.join(settings.MEDIA_ROOT, str(course_id))
        file_path = os.path.join(course_dir, lesson or '')
        if not lesson or not os.path.isfile(file_path):
            messages.error(request, "Некорректный урок.")
            return redirect('course_edit', course_id=course_id)

        try:
            with open(file_path, 'wb') as fp:
                fp.write(new_content.encode('utf-8'))
            messages.success(request, f"Урок «{lesson}» сохранён.")
        except Exception as e:
            messages.error(request, f"Ошибка при сохранении: {e}")

        return redirect(f"{request.path}?lesson={lesson}")


class ReportCourseView(View):
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


class CreateTopicView(View):
    @method_decorator(login_required)
    def post(self, request):
        name = request.POST.get('name')

        if not name:
            return JsonResponse({'status': 'error', 'error': 'no name field'})

        if Topic.objects.filter(name=name).exists():
            return JsonResponse({'status': 'error', 'error': 'topic with this name already exist'})

        topic = Topic.objects.create(name=name, author=request.user)

        return JsonResponse({'status': 'ok', 'ok': topic.id})


class GetTopicsView(View):
    @method_decorator(login_required)
    def get(self, request):
        qs = Topic.objects.order_by('name').values('id', 'name')

        return JsonResponse({'status': 'ok', 'topics': list(qs)})


class GetTopicView(View):
    @method_decorator(login_required)
    def get(self, request, topic_id):
        topic = Topic.objects.filter(id=topic_id).first()

        return JsonResponse({'status': 'ok', 'topic': topic})
