"""Auth views: signup / login / Google login / refresh / me / change-password / logout."""

from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView as SimpleJWTTokenRefreshView,
)

from apps.accounts.models import User
from apps.accounts.serializers import (
    ChangePasswordSerializer,
    GoogleLoginSerializer,
    LoginSerializer,
    LogoutSerializer,
    SignupSerializer,
    UserSerializer,
)
from apps.common.mixins import SuccessResponseMixin
from apps.common.responses import success_response


@extend_schema(tags=["Auth"])
class SignupView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SignupSerializer

    @extend_schema(summary="Register a new account and receive a JWT pair")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return success_response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            message="Account created successfully.",
            status_code=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Auth"])
class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(summary="Log in with email + password, receive a JWT pair")
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return success_response(
            response.data,
            message="Logged in successfully.",
            status_code=response.status_code,
        )


@extend_schema(tags=["Auth"])
class GoogleLoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = GoogleLoginSerializer

    @extend_schema(summary="Log in / sign up with a Google ID token (Gmail)")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return success_response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "created": serializer.created,
            },
            message="Google authentication successful.",
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Auth"])
class MeView(SuccessResponseMixin, generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    http_method_names = ["get", "patch", "put", "head", "options"]
    success_messages = {
        "retrieve": "Profile retrieved successfully.",
        "update": "Profile updated successfully.",
        "partial_update": "Profile updated successfully.",
    }

    def get_object(self):
        return self.request.user

    @extend_schema(summary="Get the current user's profile")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(summary="Update the current user's profile")
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(summary="Replace the current user's profile")
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)


@extend_schema(tags=["Auth"])
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={200: {"type": "object", "properties": {"detail": {"type": "string"}}}},
        summary="Change the current user's password",
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(message="Password changed successfully.")


@extend_schema(tags=["Auth"])
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=LogoutSerializer,
        responses={200: {"type": "object", "properties": {"detail": {"type": "string"}}}},
        summary="Blacklist a refresh token (log out)",
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(message="Logged out successfully.")


@extend_schema(tags=["Auth"], summary="Refresh the access token")
class TokenRefreshView(SuccessResponseMixin, SimpleJWTTokenRefreshView):
    """Rotate a refresh token to get a new access token."""

    success_message = "Token refreshed successfully."


__all__ = [
    "SignupView",
    "LoginView",
    "GoogleLoginView",
    "TokenRefreshView",
    "MeView",
    "ChangePasswordView",
    "LogoutView",
]
