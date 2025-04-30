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
from home.models import UserProfile, SocialNetwork, Interest
from authentication.models import User
from education.models import Courses, Stars, Report


def user_is_staff_or_moderator(user: User) -> bool:
    return True if user.is_staff or user.is_moderator else False


class HomeView(View):
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
        if request.user.is_authenticated:
            subquery = Stars.objects.filter(
                course=OuterRef('pk'),
                user=request.user
            )
            popular_courses = Courses.objects.annotate(
                stars_count=Count('stars'),
                is_stared=Exists(subquery)
            ).order_by('-stars_count')[:3]
        else:
            popular_courses = Courses.objects.annotate(
                stars_count=Count('stars')
            ).order_by('-stars_count')[:3]

        return render(request, 'home.html', {
            'popular_courses': popular_courses
        })


class ProfileView(View):
    """Страница профиля пользователя.

    :cvar get: Отображает профиль пользователя по given user_id.
    :cvar post: Обрабатывает сохранение изменений профиля или удаление аккаунта.
    """

    @method_decorator(login_required)
    def get(self, request, user_id):
        """
        Возвращает страницу профиля пользователя.

        :param request: HTTP Django request
        :param int user_id: Идентификатор пользователя
        :return: render в 'profile.html' с данными профиля и связями
        """
        profile_owner = get_object_or_404(User, id=user_id)
        user_profile, created = UserProfile.objects.get_or_create(user=profile_owner)

        content = {
            'username': profile_owner.username,
            'user_profile': user_profile,
            'social_network': SocialNetwork.objects.filter(user_profile=user_profile),
            'interest': Interest.objects.filter(user_profile=user_profile),
            'is_owner': profile_owner == request.user,
        }
        return render(request, 'profile.html', content)

    @method_decorator(login_required)
    def post(self, request, user_id):
        """
        Обрабатывает изменения профиля или удаляет аккаунт пользователя.

        :param request: HTTP Django request
        :param int user_id: Идентификатор профиля
        :return: redirect на 'profile' при сохранении или 'home' после удаления
        """
        if request.user.id != int(user_id):
            messages.error(request, "У вас нет прав на изменение этого профиля.")
            return redirect('profile', user_id=user_id)

        if request.POST.get('action') == 'delete_account':
            request.user.delete()
            logout(request)
            messages.success(request, "Ваш аккаунт удалён.")
            return redirect('home')

        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
        new_username = request.POST.get('username', '').strip()
        new_about = request.POST.get('about', '').strip()
        new_email = request.POST.get('email', '').strip()
        new_phone = request.POST.get('phone', '').strip()

        if new_username:
            request.user.username = new_username
            request.user.save()

        user_profile.about = new_about
        user_profile.email = new_email
        user_profile.phone = new_phone
        user_profile.save()

        messages.success(request, "Профиль успешно сохранён.")
        return redirect('profile', user_id=user_id)


class ModeratorPanelView(View):
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
            'reports': Report.objects.all(),
            'courses': Courses.objects.all(),
        }
        return render(request, 'moderator_page.html', context)


class AddModerator(View):
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


class DeleteUser(View):
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


class DeleteCourse(View):
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
