"""Minimal restaurant endpoint tests (menu dependency slice)."""

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Role, User

RESTAURANTS_URL = "/api/v1/restaurants/"


def _user(email="owner@example.com", password="StrongPass123!"):
    return User.objects.create_user(
        email=email, password=password, first_name="Ow", last_name="Ner"
    )


def _auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_create_restaurant_sets_owner_and_upgrades_role():
    user = _user()
    response = _auth_client(user).post(
        RESTAURANTS_URL, {"name": "Momo House", "phone": "+9779800000001"}, format="json"
    )
    assert response.status_code == 201, response.data
    assert response.data["owner"] == user.id
    assert response.data["slug"] == "momo-house"
    user.refresh_from_db()
    assert user.role == Role.RESTAURANT_OWNER


@pytest.mark.django_db
def test_anon_cannot_create_restaurant():
    assert (
        APIClient().post(RESTAURANTS_URL, {"name": "X"}, format="json").status_code
        in (401, 403)
    )


@pytest.mark.django_db
def test_restaurant_list_is_public_but_writes_are_owner_only():
    owner = _user("owner@example.com")
    _auth_client(owner).post(RESTAURANTS_URL, {"name": "Momo House"}, format="json")

    response = APIClient().get(RESTAURANTS_URL)
    assert response.status_code == 200
    assert response.data["count"] == 1

    restaurant_id = response.data["results"][0]["id"]
    stranger = _user("stranger@example.com")
    response = _auth_client(stranger).patch(
        f"{RESTAURANTS_URL}{restaurant_id}/", {"phone": "+9779800000002"}, format="json"
    )
    assert response.status_code == 403

    response = _auth_client(owner).patch(
        f"{RESTAURANTS_URL}{restaurant_id}/", {"phone": "+9779800000002"}, format="json"
    )
    assert response.status_code == 200, response.data
