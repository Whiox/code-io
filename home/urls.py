from django.urls import path
from home.views import (
    home_view, ChangeThemeView, ProfileView, MyProfileView
)

urlpatterns = [
    path('', home_view, name='home'),
    path('profile/<str:user_id>/', ProfileView.as_view(), name='profile'),
    path('my-profile/', MyProfileView.as_view(), name='my_profile'),
    path('change-theme/', ChangeThemeView.as_view(), name='change_theme'),
]
