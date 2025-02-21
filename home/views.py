from django.shortcuts import render, redirect
from django.views import View
from django.utils import timezone
from django.http import JsonResponse
from home.models import UserProfile, SocialNetwork, Interest

def home_view(request):
    current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S.%f %Z')
    content = {
        'data': current_time
    }
    return render(request, 'home.html', {'content': content})


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
            'interest': Interest.objects.filter(user_profile=user_profile)
        }

        return render(request, 'profile.html', content)


class ChangeThemeView(View):
    @staticmethod
    def post(request):
        if request.user.is_anonymous:
            return redirect('/login')

        user = request.user
        user.theme = "dark" if user.theme == "light" else "light"
        user.save()
        return JsonResponse({"status": "success", "new_theme": user.theme})
