from django.urls import path
from education.views import (
    view_course
)

urlpatterns = [
    path('course/<str:token>/', view_course, name='course'),
]
