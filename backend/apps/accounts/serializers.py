"""Serializers for signup / login / Google login / profile / password / logout."""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Role, User


class UserSerializer(serializers.ModelSerializer):
    """Public profile representation (read + self-service update)."""

    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone",
            "first_name",
            "last_name",
            "full_name",
            "avatar_url",
            "role",
            "is_verified",
            "date_joined",
            "updated_at",
        ]
        read_only_fields = ["id", "email", "role", "is_verified", "date_joined", "updated_at"]

    def get_full_name(self, obj: User) -> str:
        return obj.get_full_name()


class SignupSerializer(serializers.ModelSerializer):
    """Create a user and (in the view) issue a JWT pair."""

    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    password_confirm = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )
    role = serializers.ChoiceField(
        choices=[c for c in Role.choices if c[0] != Role.ADMIN],
        default=Role.CUSTOMER,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone",
            "first_name",
            "last_name",
            "role",
            "password",
            "password_confirm",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": False, "allow_blank": True},
            "last_name": {"required": False, "allow_blank": True},
        }

    def validate_email(self, value: str) -> str:
        return User.objects.normalize_email(value)

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        try:
            validate_password(attrs["password"])
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class LoginSerializer(TokenObtainPairSerializer):
    """Email + password login. Response adds the user + token pair."""

    username_field = "email"

    def validate(self, attrs):
        email = attrs.get("email", "")
        password = attrs.get("password", "")
        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )
        if user is None:
            raise serializers.ValidationError(
                {"detail": "No active account found with the given credentials."},
                code="authorization",
            )
        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": "This account is inactive."}, code="authorization"
            )
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,
        }


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, style={"input_type": "password"})
    new_password = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )
    new_password_confirm = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({"old_password": "Current password is incorrect."})
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "New passwords do not match."}
            )
        try:
            validate_password(attrs["new_password"], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"new_password": list(exc.messages)})
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password", "updated_at"])
        return user


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        from rest_framework_simplejwt.exceptions import TokenError

        try:
            RefreshToken(self.token).blacklist()
        except TokenError as exc:
            raise serializers.ValidationError({"refresh": str(exc)})


class GoogleLoginSerializer(serializers.Serializer):
    """Gmail login via a Google ID token (Google Identity Services).

    New emails create an account (unusable password, ``is_verified=True``);
    existing emails link and return tokens. ``role`` only applies to new
    accounts and can never create an admin.
    """

    id_token = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=[c for c in Role.choices if c[0] != Role.ADMIN],
        default=Role.CUSTOMER,
        write_only=True,
    )

    def validate(self, attrs):
        from apps.accounts.google import verify_google_id_token

        idinfo = verify_google_id_token(attrs["id_token"])
        email = idinfo.get("email")
        if not email:
            raise serializers.ValidationError({"id_token": "Google token has no email."})
        if not idinfo.get("email_verified"):
            raise serializers.ValidationError(
                {"id_token": "Google email address is not verified."}
            )
        attrs["idinfo"] = idinfo
        attrs["email"] = User.objects.normalize_email(email)
        return attrs

    def save(self, **kwargs):
        idinfo = self.validated_data["idinfo"]
        email = self.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                raise serializers.ValidationError(
                    {"detail": "This account is inactive."}
                )
            updated = []
            if idinfo.get("email_verified") and not user.is_verified:
                user.is_verified = True
                updated.append("is_verified")
            if not user.first_name and idinfo.get("given_name"):
                user.first_name = idinfo["given_name"][:150]
                updated.append("first_name")
            if not user.last_name and idinfo.get("family_name"):
                user.last_name = idinfo["family_name"][:150]
                updated.append("last_name")
            if not user.avatar_url and idinfo.get("picture"):
                user.avatar_url = idinfo["picture"][:500]
                updated.append("avatar_url")
            if updated:
                user.save(update_fields=[*updated, "updated_at"])
            self.created = False
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=email,
                password=None,
                first_name=(idinfo.get("given_name") or "")[:150],
                last_name=(idinfo.get("family_name") or "")[:150],
                avatar_url=(idinfo.get("picture") or "")[:500],
                role=self.validated_data.get("role", Role.CUSTOMER),
                is_verified=True,
            )
            self.created = True
        self.instance = user
        return user
