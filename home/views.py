from django.shortcuts import render
from django.utils import timezone
def home_view(request):
    current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S.%f %Z')
    content = {
        'data': current_time
    }
    return render(request, 'home.html', {'content': content})