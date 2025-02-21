from django.urls import path
from home.views import (
    home_view, ChangeThemeView, MyProfileView
)

urlpatterns = [
    path('', home_view, name='home'),
    path('my-profile', MyProfileView.as_view(), name='my_profile'),
    path('change-theme/', ChangeThemeView.as_view(), name='change_theme'),
]
