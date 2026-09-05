"""Auth flow tests: signup / login / refresh / me / password / logout."""

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User

SIGNUP_URL = "/api/v1/auth/signup/"
LOGIN_URL = "/api/v1/auth/login/"
REFRESH_URL = "/api/v1/auth/token/refresh/"
ME_URL = "/api/v1/auth/me/"
CHANGE_PASSWORD_URL = "/api/v1/auth/change-password/"
LOGOUT_URL = "/api/v1/auth/logout/"

PASSWORD = "StrongPass123!"


def _signup(client, **overrides):
    payload = {
        "email": "customer@example.com",
        "password": PASSWORD,
        "password_confirm": PASSWORD,
        "first_name": "Test",
        "last_name": "User",
    }
    payload.update(overrides)
    return client.post(SIGNUP_URL, payload, format="json")


@pytest.mark.django_db
def test_signup_returns_user_and_jwt_pair():
    client = APIClient()
    response = _signup(client)
    assert response.status_code == 201, response.data
    assert response.data["user"]["email"] == "customer@example.com"
    assert response.data["user"]["role"] == "customer"
    assert response.data["access"] and response.data["refresh"]
    assert User.objects.filter(email="customer@example.com").exists()


@pytest.mark.django_db
def test_signup_with_role():
    client = APIClient()
    response = _signup(client, email="owner@example.com", role="restaurant_owner")
    assert response.status_code == 201, response.data
    assert response.data["user"]["role"] == "restaurant_owner"


@pytest.mark.django_db
def test_signup_rejects_admin_role_and_mismatch_and_duplicate():
    client = APIClient()
    assert _signup(client, email="a@example.com", role="admin").status_code == 400
    assert (
        _signup(client, email="b@example.com", password_confirm="Other123!").status_code
        == 400
    )
    assert _signup(client, email="dup@example.com").status_code == 201
    assert _signup(client, email="dup@example.com").status_code == 400


@pytest.mark.django_db
def test_login_returns_tokens_and_user():
    _signup(APIClient(), email="login@example.com")
    response = APIClient().post(
        LOGIN_URL, {"email": "login@example.com", "password": PASSWORD}, format="json"
    )
    assert response.status_code == 200, response.data
    assert response.data["access"] and response.data["refresh"]
    assert response.data["user"]["email"] == "login@example.com"


@pytest.mark.django_db
def test_login_rejects_bad_credentials():
    _signup(APIClient(), email="bad@example.com")
    client = APIClient()
    assert (
        client.post(
            LOGIN_URL, {"email": "bad@example.com", "password": "Wrong123!"}, format="json"
        ).status_code
        == 400
    )
    assert (
        client.post(
            LOGIN_URL, {"email": "missing@example.com", "password": PASSWORD}, format="json"
        ).status_code
        == 400
    )


@pytest.mark.django_db
def test_me_requires_auth_and_supports_get_patch():
    assert APIClient().get(ME_URL).status_code in (401, 403)

    client = APIClient()
    tokens = _signup(client, email="me@example.com").data
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

    response = client.get(ME_URL)
    assert response.status_code == 200
    assert response.data["email"] == "me@example.com"

    response = client.patch(ME_URL, {"first_name": "New", "phone": "+10000000001"}, format="json")
    assert response.status_code == 200, response.data
    assert response.data["first_name"] == "New"

    # Role escalation via profile update is not allowed (read-only).
    response = client.patch(ME_URL, {"role": "admin"}, format="json")
    assert response.status_code == 200
    assert response.data["role"] == "customer"


@pytest.mark.django_db
def test_change_password_and_relogin():
    client = APIClient()
    tokens = _signup(client, email="pw@example.com").data
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

    response = client.post(
        CHANGE_PASSWORD_URL,
        {
            "old_password": PASSWORD,
            "new_password": "BrandNew123!",
            "new_password_confirm": "BrandNew123!",
        },
        format="json",
    )
    assert response.status_code == 200, response.data

    # Old password no longer works, new one does.
    anon = APIClient()
    assert (
        anon.post(
            LOGIN_URL, {"email": "pw@example.com", "password": PASSWORD}, format="json"
        ).status_code
        == 400
    )
    assert (
        anon.post(
            LOGIN_URL, {"email": "pw@example.com", "password": "BrandNew123!"}, format="json"
        ).status_code
        == 200
    )


@pytest.mark.django_db
def test_refresh_and_logout_blacklists_token():
    client = APIClient()
    tokens = _signup(client, email="sess@example.com").data

    response = client.post(REFRESH_URL, {"refresh": tokens["refresh"]}, format="json")
    assert response.status_code == 200, response.data
    rotated_refresh = response.data["refresh"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    response = client.post(LOGOUT_URL, {"refresh": rotated_refresh}, format="json")
    assert response.status_code == 200, response.data

    # Blacklisted refresh token can no longer be used.
    assert client.post(REFRESH_URL, {"refresh": rotated_refresh}, format="json").status_code == 401
