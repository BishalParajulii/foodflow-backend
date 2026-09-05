"""Admin for the custom User model."""

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from apps.accounts.models import User


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone", "role")

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            "email",
            "phone",
            "first_name",
            "last_name",
            "avatar_url",
            "role",
            "password",
            "is_verified",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ("email", "get_full_name", "role", "is_active", "is_staff", "date_joined")
    list_filter = ("role", "is_staff", "is_superuser", "is_active", "is_verified")
    search_fields = ("email", "first_name", "last_name", "phone")
    ordering = ("-date_joined",)
    readonly_fields = ("last_login", "date_joined", "updated_at")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone", "avatar_url", "role")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_verified",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "phone",
                    "role",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
