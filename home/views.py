from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils import timezone
from django.http import JsonResponse
from home.models import UserProfile, SocialNetwork, Interest
from authentication.models import User

def home_view(request):
    current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S.%f %Z')
    content = {
        'data': current_time
    }
    return render(request, 'home.html', {'content': content})


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
