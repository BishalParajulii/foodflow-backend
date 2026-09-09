"""Auth URL namespace: /api/v1/auth/."""

from django.urls import path

from apps.accounts.views import (
    ChangePasswordView,
    GoogleLoginView,
    LoginView,
    LogoutView,
    MeView,
    SignupView,
    TokenRefreshView,
)

app_name = "accounts"

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("google/", GoogleLoginView.as_view(), name="google-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
