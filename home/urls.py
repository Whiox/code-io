"""home urls"""

from django.urls import path
from home.views import (
    HomeView, ProfileView)


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('profile/<str:user_id>/', ProfileView.as_view(), name='profile'),
]
