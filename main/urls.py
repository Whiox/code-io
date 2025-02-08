from django.urls import path
from main.views import home, my_courses, all_courses, add_course

urlpatterns = [
    path('', home, name='home'),  # Главная страница
    path('my-courses/', my_courses, name='my_courses'),  # Мои курсы
    path('all-courses/', all_courses, name='all_courses'),  # Все курсы
    path('add-courses/', add_course, name='add_courses'),  # Добавить курс
]
