"""Gmail login tests (Google ID token -> JWT pair)."""

from unittest.mock import patch

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from apps.accounts.models import User

GOOGLE_URL = "/api/v1/auth/google/"
SIGNUP_URL = "/api/v1/auth/signup/"
PASSWORD = "StrongPass123!"

GOOGLE_CLAIMS = {
    "iss": "https://accounts.google.com",
    "aud": "test-client-id",
    "sub": "110169484474386276334",
    "email": "guser@example.com",
    "email_verified": True,
    "given_name": "Goo",
    "family_name": "Gle",
    "picture": "https://example.com/avatar.jpg",
}


def _google_post(client, **payload):
    data = {"id_token": "fake-google-id-token"}
    data.update(payload)
    return client.post(GOOGLE_URL, data, format="json")


@override_settings(GOOGLE_CLIENT_ID="test-client-id")
@pytest.mark.django_db
def test_google_login_creates_new_verified_user():
    client = APIClient()
    with patch(
        "apps.accounts.google.verify_google_id_token", return_value=dict(GOOGLE_CLAIMS)
    ):
        response = _google_post(client)
    assert response.status_code == 200, response.data
    assert response.data["created"] is True
    assert response.data["user"]["email"] == "guser@example.com"
    assert response.data["user"]["is_verified"] is True
    assert response.data["user"]["first_name"] == "Goo"
    assert response.data["access"] and response.data["refresh"]

    user = User.objects.get(email="guser@example.com")
    assert user.is_verified is True
    assert not user.has_usable_password()
    assert user.avatar_url == "https://example.com/avatar.jpg"


@override_settings(GOOGLE_CLIENT_ID="test-client-id")
@pytest.mark.django_db
def test_google_login_links_existing_password_user():
    client = APIClient()
    client.post(
        SIGNUP_URL,
        {
            "email": "guser@example.com",
            "password": PASSWORD,
            "password_confirm": PASSWORD,
        },
        format="json",
    )
    with patch(
        "apps.accounts.google.verify_google_id_token", return_value=dict(GOOGLE_CLAIMS)
    ):
        response = _google_post(client)
    assert response.status_code == 200, response.data
    assert response.data["created"] is False
    assert response.data["access"] and response.data["refresh"]

    user = User.objects.get(email="guser@example.com")
    assert user.has_usable_password()  # password login still works
    assert user.is_verified is True  # Google verification carries over


@override_settings(GOOGLE_CLIENT_ID="test-client-id")
@pytest.mark.django_db
def test_google_login_rejects_unverified_email():
    claims = dict(GOOGLE_CLAIMS, email_verified=False)
    with patch("apps.accounts.google.verify_google_id_token", return_value=claims):
        response = _google_post(APIClient())
    assert response.status_code == 400


@override_settings(GOOGLE_CLIENT_ID="test-client-id")
@pytest.mark.django_db
def test_google_login_rejects_invalid_token():
    from rest_framework import serializers

    with patch(
        "apps.accounts.google.verify_google_id_token",
        side_effect=serializers.ValidationError({"id_token": "Invalid Google token: bad"}),
    ):
        response = _google_post(APIClient(), id_token="bogus")
    assert response.status_code == 400


@override_settings(GOOGLE_CLIENT_ID="")
@pytest.mark.django_db
def test_google_login_requires_client_id_configuration():
    response = _google_post(APIClient())
    assert response.status_code == 400
    assert "not configured" in str(response.data)
