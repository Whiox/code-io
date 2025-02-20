from django.urls import path
from education.views import (
    ViewCourseView, AllCoursesView, StaredCoursesView, AddCourseView, MyCoursesView, DeleteCourseView, AddStar
)

urlpatterns = [
    path('all/', AllCoursesView.as_view(), name='all'),
    path('stared/', StaredCoursesView.as_view(), name='stared'),
    path('<str:course_id>/', ViewCourseView.as_view(), name='course'),
    path('add', AddCourseView.as_view(), name='add_course'),
    path('my', MyCoursesView.as_view(), name='my_courses'),
    path('delete/<int:course_id>/', DeleteCourseView.as_view(), name='delete'),
    path('add-star/<int:course_id>/', AddStar.as_view(), name='add_star'),
]
