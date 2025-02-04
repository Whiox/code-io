from django.urls import path
from main.views import home, my_courses, all_courses, add_courses

urlpatterns = [
    path('', home, name='home'),  # Главная страница
    path('my-courses/', my_courses, name='my_courses'),  # Мои курсы
    path('all-courses/', all_courses, name='all_courses'),  # Все курсы
    path('add-courses/', add_courses, name='add_courses'),  # Добавить курс
]
