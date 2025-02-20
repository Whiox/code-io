from django.shortcuts import render, redirect
from django.views import View
from django.utils import timezone
from django.http import JsonResponse

def home_view(request):
    current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S.%f %Z')
    content = {
        'data': current_time
    }
    return render(request, 'home.html', {'content': content})


class ChangeThemeView(View):
    @staticmethod
    def post(request):
        if request.user.is_anonymous:
            return redirect('/login')

        user = request.user
        user.theme = "dark" if user.theme == "light" else "light"
        user.save()
        return JsonResponse({"status": "success", "new_theme": user.theme})
