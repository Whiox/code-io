"""education urls"""

from django.urls import path
from education.views import (
    AllCoursesView, StaredCoursesView, ViewCourseView,
    AddCourseView, CourseEditorView,
    MyCoursesView, DeleteCourseView, AdminCoursesView,
    AddStar, ReportCourseView, LessonProgress, CourseProgressList,
    CreateTopicView, GetTopicsView, GetTopicView
)

urlpatterns = [
    path('all/', AllCoursesView.as_view(), name='all'),
    path('stared/', StaredCoursesView.as_view(), name='stared'),
    path('add', AddCourseView.as_view(), name='add_course'),
    path('my', MyCoursesView.as_view(), name='my_courses'),
    path('users/courses', AdminCoursesView.as_view(), name='users_courses'),

    path('<int:course_id>/', ViewCourseView.as_view(), name='course'),
    path('<int:course_id>/progress/', CourseProgressList.as_view(), name='progress'),
    path('<int:course_id>/<int:lesson_id>/progress/', LessonProgress.as_view(), name='lesson_progress'),

    path('delete/<int:course_id>/', DeleteCourseView.as_view(), name='delete'),
    path('add-star/<int:course_id>/', AddStar.as_view(), name='add_star'),
    path('course/<int:course_id>/edit/', CourseEditorView.as_view(), name='course_edit'),
    path('<int:course_id>/report/', ReportCourseView.as_view(), name='course_report'),

    path('topic/create', CreateTopicView.as_view(), name='create_topic'),
    path('topics/', GetTopicsView.as_view(), name='get_topics'),
    path('topic/', GetTopicView.as_view(), name='get_topic'),
]
