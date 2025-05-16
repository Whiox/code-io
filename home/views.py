"""
Views, необходимые для общей картины сайта.
"""
import os
import shutil

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.db.models.aggregates import Count
from django.http import JsonResponse, QueryDict
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from code_io import settings
from code_io.mixins import LoggingMixin
from home.models import UserProfile, SocialNetwork, Technology
from authentication.models import User
from education.methods import get_most_popular_courses
from education.models import Courses, Stars, ReportCourse, Topic, ReportTopic


def user_is_staff_or_moderator(user: User) -> bool:
    return True if user.is_staff or user.is_moderator else False


class HomeView(LoggingMixin, View):
    """Главная страница сайта.

    :cvar get: Отображает три самых популярных курса (с учётом отмеченных звёздочкой).
    """

    @staticmethod
    def get(request):
        """
        Возвращает главную страницу с тремя самыми популярными курсами.

        :param request: HTTP Django request
        :return: render в 'home.html' с контекстом popular_courses
        """
        popular_courses = get_most_popular_courses(request.user)

        return render(request, 'home.html', {
            'popular_courses': popular_courses
        })


class ProfileView(View):
    """Страница профиля пользователя."""

    @method_decorator(login_required)
    def get(self, request, user_id):
        profile_owner = get_object_or_404(User, id=user_id)
        user_profile, _ = UserProfile.objects.get_or_create(user=profile_owner)

        content = {
            'username': profile_owner.username,
            'user_profile': user_profile,
            'social_network': SocialNetwork.objects.filter(user_profile=user_profile),
            'interest': Technology.objects.filter(user_profile=user_profile),
            'is_owner': profile_owner == request.user,
        }
        return render(request, 'profile.html', content)

    @method_decorator(login_required)
    def post(self, request, user_id):
        if request.user.id != int(user_id):
            messages.error(request, "У вас нет прав на изменение этого профиля.")
            return redirect('profile', user_id=user_id)

        if request.POST.get('action') == 'delete_account':
            request.user.delete()
            logout(request)
            messages.success(request, "Ваш аккаунт удалён.")
            return redirect('home')

        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

        avatar_file = request.FILES.get('avatar')
        if avatar_file:
            if user_profile.avatar:
                user_profile.avatar.delete(save=False)
            user_profile.avatar = avatar_file

        new_username = request.POST.get('username', '').strip()
        if new_username:
            request.user.username = new_username
            request.user.save()
        user_profile.about = request.POST.get('about', '').strip()
        user_profile.email = request.POST.get('email', '').strip()
        user_profile.save()

        Technology.objects.filter(user_profile=user_profile).delete()
        tech_list = request.POST.getlist('technologies')
        for label in [t.strip() for t in tech_list if t.strip()]:
            Technology.objects.create(user_profile=user_profile, label=label)

        SocialNetwork.objects.filter(user_profile=user_profile).delete()
        sn_labels = request.POST.getlist('sn_label')
        sn_links = request.POST.getlist('sn_linc')
        for label, link in zip(sn_labels, sn_links):
            if label.strip() and link.strip():
                SocialNetwork.objects.create(
                    user_profile=user_profile,
                    label=label.strip(),
                    linc=link.strip()
                )

        messages.success(request, "Профиль успешно обновлён.")
        return redirect('profile', user_id=user_id)


class ModeratorPanelView(LoggingMixin, View):
    """Панель модератора для просмотра пользователей, жалоб и курсов.

    :cvar get: Отображает страницу с таблицами users, reports, courses.
    """

    @method_decorator(login_required)
    def get(self, request):
        """
        Формирует контекст для панели модерации и рендерит шаблон.

        :param request: HTTP-запрос Django
        :return: render 'moderator_page.html' с контекстом:
                 - users: QuerySet всех пользователей
                 - reports: QuerySet всех жалоб
                 - courses: QuerySet всех курсов
        """
        if not user_is_staff_or_moderator(request.user):
            return redirect('home')

        context = {
            'users': User.objects.all(),
            'courses': Courses.objects.all().select_related('author'),
            'topics': Topic.objects.filter(author__isnull=False).select_related('author'),
            'course_reports': ReportCourse.objects.all().select_related('author', 'course'),
            'topic_reports': ReportTopic.objects.all().select_related('author', 'course')
        }

        return render(request, 'moderator_page.html', context)


class AddModerator(LoggingMixin, View):
    """Назначение и снятие статуса модератора для пользователя.

    :cvar post: Сделать пользователя модератором.
    :cvar delete: Убрать у пользователя статус модератора.
    """

    @method_decorator(login_required)
    def post(self, request):
        """
        Назначает пользователю роль модератора.

        Ожидает в body: user_id.

        :param request: HTTP-запрос Django
        :return: JsonResponse {'status':'ok','ok':user.id} или {'status':'error',...}
        """
        if not request.user.is_staff:
            return JsonResponse({'status': 'error', 'error': 'you must be staff'})

        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)

        user.is_moderator = True
        user.save()
        return JsonResponse({'status': 'ok', 'ok': user.id})

    @method_decorator(login_required)
    def delete(self, request):
        """
        Убирает у пользователя роль модератора.

        Ожидает в body: user_id.

        :param request: HTTP-запрос Django
        :return: JsonResponse {'status':'ok','ok':user.id} или {'status':'error',...}
        """
        if not request.user.is_staff:
            return JsonResponse({'status': 'error', 'error': 'you must be staff'})

        data = QueryDict(request.body.decode('utf-8'))
        user_id = data.get('user_id')
        user = get_object_or_404(User, id=user_id)

        user.is_moderator = False
        user.save()
        return JsonResponse({'status': 'ok', 'ok': user.id})


class DeleteUser(LoggingMixin, View):
    """Удаление пользователя модератором или staff."""

    @method_decorator(login_required)
    def delete(self, request):
        """
        Удаляет указанного пользователя.

        Только staff или модератор может удалять обычных пользователей;
        только staff может удалять модераторов и других staff.

        Ожидает в body: user_id.

        :param request: HTTP-запрос Django
        :return: JsonResponse {'status':'ok'} или {'status':'error',...}
        """
        if not user_is_staff_or_moderator(request.user):
            return JsonResponse({'status': 'error', 'error': 'you must be staff or moderator'})

        data = QueryDict(request.body.decode('utf-8'))
        user_id = data.get('user_id')
        user = get_object_or_404(User, id=user_id)

        if (user.is_moderator or user.is_staff) and not request.user.is_staff:
            return JsonResponse({'status': 'error', 'error': 'only staff can delete moderator or staff'})

        user.delete()
        return JsonResponse({'status': 'ok', 'ok': 'success deleting'})


class DeleteCourse(LoggingMixin, View):
    """Удаление курса модератором или staff-пользователем."""

    @method_decorator(login_required)
    def delete(self, request):
        """
        Удаляет курс и папку с его уроками на диске.

        Ожидает в body: course_id.

        :param request: HTTP-запрос Django
        :return: JsonResponse {'status':'ok'} или {'status':'error',...}
        """
        if not user_is_staff_or_moderator(request.user):
            return JsonResponse({'status': 'error', 'error': 'you must be staff or moderator'})

        data = QueryDict(request.body.decode('utf-8'))
        course_id = data.get('course_id')
        course = get_object_or_404(Courses, course_id=course_id)

        course_folder = os.path.join(settings.MEDIA_ROOT, str(course.course_id))
        if os.path.exists(course_folder):
            shutil.rmtree(course_folder)

        course.delete()
        return JsonResponse({'status': 'ok', 'ok': 'success deleting'})


class DeleteCourseReport(LoggingMixin, View):
    """Удаление жалобы на курсы модератором или staff-пользователем."""

    @method_decorator(login_required)
    def delete(self, request):
        """
        Удаляет жалобу.

        Ожидает в body: report_id.

        :param request: HTTP-запрос Django
        :return: JsonResponse {'status':'ok'} или {'status':'error',...}
        """
        if not user_is_staff_or_moderator(request.user):
            return JsonResponse({'status': 'error', 'error': 'you must be staff or moderator'})

        data = QueryDict(request.body.decode('utf-8'))
        report_id = data.get('report_id')
        report = get_object_or_404(ReportCourse, id=report_id)

        report.delete()
        return JsonResponse({'status': 'ok', 'ok': 'success deleting'})


class DeleteTopic(LoggingMixin, View):
    """Удаление топика модератором или staff-пользователем."""

    @method_decorator(login_required)
    def delete(self, request):
        """
        Удаляет топик.

        Ожидает в body: topic_id.

        :param request: HTTP-запрос Django
        :return: JsonResponse {'status':'ok'} или {'status':'error',...}
        """
        if not user_is_staff_or_moderator(request.user):
            return JsonResponse({'status': 'error', 'error': 'you must be staff or moderator'})

        data = QueryDict(request.body.decode('utf-8'))
        topic_id = data.get('topic_id')
        topic = get_object_or_404(Topic, id=topic_id)

        topic.delete()
        return JsonResponse({'status': 'ok', 'ok': 'success deleting'})


class DeleteTopicReport(LoggingMixin, View):
    """Удаление жалобы на темы модератором или staff-пользователем."""

    @method_decorator(login_required)
    def delete(self, request):
        """
        Удаляет жалобу.

        Ожидает в body: report_id.

        :param request: HTTP-запрос Django
        :return: JsonResponse {'status':'ok'} или {'status':'error',...}
        """
        if not user_is_staff_or_moderator(request.user):
            return JsonResponse({'status': 'error', 'error': 'you must be staff or moderator'})

        data = QueryDict(request.body.decode('utf-8'))
        report_id = data.get('report_id')
        report = get_object_or_404(ReportTopic, id=report_id)

        report.delete()
        return JsonResponse({'status': 'ok', 'ok': 'success deleting'})


def error404(request, exc):
    return render(request, '404.html')
