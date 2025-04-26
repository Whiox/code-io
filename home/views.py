from django.contrib import messages
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
    @staticmethod
    def get(request):
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
    @method_decorator(login_required)
    def get(self, request, user_id):
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
        if request.user.id != int(user_id):
            messages.error(request, "У вас нет прав на редактирование этого профиля.")
            return redirect('profile', user_id=user_id)

        profile_owner = request.user
        user_profile, _ = UserProfile.objects.get_or_create(user=profile_owner)

        new_username = request.POST.get('username', '').strip()
        new_about    = request.POST.get('about', '').strip()
        new_email    = request.POST.get('email', '').strip()
        new_phone    = request.POST.get('phone', '').strip()

        if new_username:
            profile_owner.username = new_username
        profile_owner.save()

        user_profile.about = new_about
        user_profile.email = new_email
        user_profile.phone = new_phone
        user_profile.save()

        messages.success(request, "Профиль успешно сохранён.")
        return redirect('profile', user_id=user_id)