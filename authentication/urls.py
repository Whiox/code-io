from django.urls import path
from authentication.views import RegisterView, LoginView, ResetPasswordView, ResetPasswordConfirmView, ChangePasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('reset/', ResetPasswordView.as_view(), name='reset_password'),
    path('reset/<uidb64>/', ResetPasswordConfirmView.as_view(), name='reset_password_confirm'),
    path('change', ChangePasswordView.as_view(), name='change_password')
]
