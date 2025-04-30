"""home urls"""

from django.urls import path
from home.views import (
    HomeView, ProfileView,
    ModeratorPanelView, AddModerator,
    DeleteUser, DeleteCourse, DeleteReport
)


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('profile/<str:user_id>/', ProfileView.as_view(), name='profile'),
    path('moderator/', ModeratorPanelView.as_view(), name='moderator'),
    path('moderator/add/moderator/', AddModerator.as_view(), name='add_moderator'),
    path('moderator/delete/user/', DeleteUser.as_view(), name='delete_user'),
    path('moderator/delete/course/', DeleteCourse.as_view(), name='delete_course'),
    path('moderator/delete/report/', DeleteReport.as_view(), name='delete_report'),
]
