from django.shortcuts import render


def home(request):
    return render(request, 'home.html')

def my_courses(request):
    # Здесь вы можете добавить логику для получения курсов пользователя
    return render(request, 'my_courses.html')

def all_courses(request):
    # Здесь вы можете добавить логику для получения всех курсов
    return render(request, 'all_courses.html')
