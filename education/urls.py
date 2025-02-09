from django.urls import path
from education.views import (
    view_course, all_courses
)

urlpatterns = [
    path('course/all/', all_courses, name='all'),
    path('course/<str:token>/', view_course, name='course'),
]
