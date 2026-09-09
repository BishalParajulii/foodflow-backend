"""Branch tests: nested under restaurant, owner/admin only."""

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.restaurants.models import Branch, Restaurant


def _user(email, password="StrongPass123!", **extra):
    return User.objects.create_user(email=email, password=password, **extra)


def _auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def owner(db):
    return _user("owner@example.com")


@pytest.fixture
def stranger(db):
    return _user("stranger@example.com")


@pytest.fixture
def staff(db):
    return _user("staff@example.com", is_staff=True)


@pytest.fixture
def platform_admin(db):
    return _user("admin@example.com", role=Role.ADMIN)


@pytest.fixture
def restaurant(owner):
    return Restaurant.objects.create(name="Momo House", owner=owner)


def _branches_url(restaurant_id):
    return f"/api/v1/restaurants/{restaurant_id}/branches/"


@pytest.mark.django_db
def test_owner_can_crud_branches(owner, restaurant):
    client = _auth_client(owner)
    url = _branches_url(restaurant.id)

    response = client.post(
        url,
        {"name": "Thamel Outlet", "address": "Thamel, Kathmandu", "phone": "+9779800000001"},
        format="json",
    )
    assert response.status_code == 201, response.data
    data = response.data["data"]
    assert data["slug"] == "thamel-outlet"
    assert str(data["restaurant"]) == str(restaurant.id)
    branch_id = data["id"]

    assert client.get(url).data["data"]["count"] == 1

    response = client.patch(
        f"{url}{branch_id}/", {"phone": "+9779800000002"}, format="json"
    )
    assert response.status_code == 200, response.data

    assert client.delete(f"{url}{branch_id}/").status_code == 204
    assert not Branch.objects.filter(pk=branch_id).exists()


@pytest.mark.django_db
def test_branch_access_denied_for_anon_and_stranger(restaurant, stranger):
    url = _branches_url(restaurant.id)
    assert APIClient().get(url).status_code in (401, 403)
    assert APIClient().post(url, {"name": "X"}, format="json").status_code in (401, 403)
    assert _auth_client(stranger).get(url).status_code == 403
    assert (
        _auth_client(stranger).post(url, {"name": "X"}, format="json").status_code
        == 403
    )


@pytest.mark.django_db
def test_staff_and_platform_admin_can_manage(staff, platform_admin, restaurant):
    for user in (staff, platform_admin):
        response = _auth_client(user).post(
            _branches_url(restaurant.id), {"name": f"Outlet {user.email}"}, format="json"
        )
        assert response.status_code == 201, (user.email, response.data)
    assert Branch.objects.filter(restaurant=restaurant).count() == 2


@pytest.mark.django_db
def test_branches_scoped_to_parent_restaurant(owner):
    mine = Restaurant.objects.create(name="Mine", owner=owner)
    other_owner = _user("other@example.com")
    theirs = Restaurant.objects.create(name="Theirs", owner=other_owner)
    branch = Branch.objects.create(restaurant=theirs, name="Secret Outlet")

    client = _auth_client(owner)
    # Another restaurant's branch is invisible under mine.
    assert client.get(_branches_url(mine.id)).data["data"]["count"] == 0
    assert client.get(f"{_branches_url(mine.id)}{branch.id}/").status_code == 404
    # Unknown restaurant is 404, not 403 (no info leak about existence).
    assert client.get(_branches_url(9999)).status_code == 404


@pytest.mark.django_db
def test_branch_slugs_unique_per_restaurant(owner, restaurant):
    client = _auth_client(owner)
    url = _branches_url(restaurant.id)
    assert client.post(url, {"name": "Thamel"}, format="json").status_code == 201
    response = client.post(url, {"name": "Thamel"}, format="json")
    assert response.status_code == 201
    assert response.data["data"]["slug"] == "thamel-2"


@pytest.mark.django_db
def test_restaurant_detail_nests_branches(owner, restaurant):
    Branch.objects.create(restaurant=restaurant, name="Thamel Outlet")
    Branch.objects.create(restaurant=restaurant, name="Lalitpur Outlet")
    response = _auth_client(owner).get(f"/api/v1/restaurants/{restaurant.id}/")
    assert response.status_code == 200
    assert response.data["data"]["branches_count"] == 2
    assert {b["name"] for b in response.data["data"]["branches"]} == {
        "Thamel Outlet",
        "Lalitpur Outlet",
    }
