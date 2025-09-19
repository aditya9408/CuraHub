from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, 
    ProfileView, CustomTokenRefreshView
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
]