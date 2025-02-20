from django.urls import path
from home.views import (
    home_view, ChangeThemeView
)

urlpatterns = [
    path('', home_view, name='home'),
    path('change-theme/', ChangeThemeView.as_view(), name='change_theme'),
]
