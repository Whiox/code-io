"""Пути, связанные с аунтефикацией"""

from django.urls import path
from authentication.views import (
    RegisterView, LoginView, LogoutView,
    ResetPasswordView, ResetPasswordConfirmView,
    ChangePasswordView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('reset/', ResetPasswordView.as_view(), name='reset_password'),
    path('reset/<str:token>/', ResetPasswordConfirmView.as_view(), name='reset_password_confirm'),
    path('change/', ChangePasswordView.as_view(), name='change_password')
]
