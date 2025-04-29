"""
Views, необходимые для общей картины сайта.
"""

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.db.models.aggregates import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from home.models import UserProfile, SocialNetwork, Interest
from authentication.models import User
from education.models import Courses, Stars


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
