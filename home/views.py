from django.db.models import Exists, OuterRef
from django.db.models.aggregates import Count
from django.shortcuts import render, redirect, get_object_or_404
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
    @staticmethod
    def get(request, user_id):
        profile_owner = get_object_or_404(User, id=user_id)
        user_profile, created = UserProfile.objects.get_or_create(user=profile_owner)

        content = {
            'username': profile_owner.username,
            'user_profile': user_profile,
            'social_network': SocialNetwork.objects.filter(user_profile=user_profile),
            'interest': Interest.objects.filter(user_profile=user_profile),
            'is_owner': True if profile_owner == request.user else False
        }

        return render(request, 'profile.html', content)


class MyProfileView(View):
    @staticmethod
    def get(request):
        if request.user.is_anonymous:
            return redirect('/login')

        user_profile, created = UserProfile.objects.get_or_create(user=request.user)

        content = {
            'username': request.user.username,
            'user_profile': user_profile,
            'social_network': SocialNetwork.objects.filter(user_profile=user_profile),
            'interest': Interest.objects.filter(user_profile=user_profile),
            'is_owner': True
        }
        return render(request, 'profile.html', content)

    @staticmethod
    def post(request):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)

        username = request.POST.get('username')
        about = request.POST.get('about')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        user_profile.about = about
        user_profile.email = email
        user_profile.phone = phone
        user_profile.save()
        content = {
            'username': request.user.username,
            'user_profile': user_profile,
            'social_network': SocialNetwork.objects.filter(user_profile=user_profile),
            'interest': Interest.objects.filter(user_profile=user_profile),
            'is_owner': True
        }
        return render(request, 'profile.html', content)
