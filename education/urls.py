from django.urls import path
from education.views import (
    view_course, all_courses,add_course
)

urlpatterns = [
    path('course/all/', all_courses, name='all'),
    path('course/<str:token>/', view_course, name='course'),
    path('add', add_course, name='add_course'),
]
