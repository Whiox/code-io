from django.urls import path
from education.views import (
    CourseViewer,
    CourseManager
)

urlpatterns = [
    path('course/all/', CourseViewer.all_courses, name='all'),
    path('course/<str:token>/', CourseViewer.view_course, name='course'),
    path('add/', CourseManager.add_course, name='add_course'),
    path('my_courses/', CourseViewer.my_courses, name='my_courses'),
    path('delete/<int:course_id>/', CourseManager.delete_course, name='delete'),
]

