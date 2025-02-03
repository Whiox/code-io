from django.urls import path
from authentication.views import RegisterView, LoginView
from main.views import home, my_courses, all_courses, add_courses

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('', home, name='home'),  # Главная страница
    path('my-courses/', my_courses, name='my_courses'),  # Мои курсы
    path('all-courses/', all_courses, name='all_courses'),  # Все курсы
     path('add-courses/', add_courses, name='add_courses'),  # Добавить курс
]
