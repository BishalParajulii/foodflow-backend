"""createadmin command tests: idempotent bootstrap of the platform admin."""

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from apps.accounts.models import Role

DEFAULT_EMAIL = "admin@foodflow.local"
DEFAULT_PASSWORD = "admin123"


@pytest.mark.django_db
def test_createadmin_creates_staff_superuser():
    call_command("createadmin")
    user = get_user_model().objects.get(email=DEFAULT_EMAIL)
    assert user.is_active
    assert user.is_staff
    assert user.is_superuser
    assert user.role == Role.ADMIN
    assert user.check_password(DEFAULT_PASSWORD)


@pytest.mark.django_db
def test_createadmin_is_idempotent():
    call_command("createadmin")
    call_command("createadmin")
    assert get_user_model().objects.filter(email=DEFAULT_EMAIL).count() == 1


@pytest.mark.django_db
def test_createadmin_keeps_existing_password_by_default():
    User = get_user_model()
    User.objects.create_user(email=DEFAULT_EMAIL, password="keepme123!")
    call_command("createadmin")
    user = User.objects.get(email=DEFAULT_EMAIL)
    assert user.check_password("keepme123!")
    assert user.is_staff and user.is_superuser


@pytest.mark.django_db
def test_createadmin_update_password_flag():
    User = get_user_model()
    User.objects.create_user(email=DEFAULT_EMAIL, password="keepme123!")
    call_command("createadmin", "--update-password")
    user = User.objects.get(email=DEFAULT_EMAIL)
    assert user.check_password(DEFAULT_PASSWORD)


@pytest.mark.django_db
def test_createadmin_honours_env_overrides(monkeypatch):
    monkeypatch.setenv("DJANGO_ADMIN_EMAIL", "boss@foodflow.local")
    monkeypatch.setenv("DJANGO_ADMIN_PASSWORD", "envpass123!")
    call_command("createadmin")
    user = get_user_model().objects.get(email="boss@foodflow.local")
    assert user.check_password("envpass123!")
    assert user.is_superuser