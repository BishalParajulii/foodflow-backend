"""Menu tests: categories / items / modifiers, public read + owner write."""

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.menu.models import Category, MenuItem, ModifierGroup, ModifierOption
from apps.restaurants.models import Restaurant

CATEGORIES_URL = "/api/v1/menu/categories/"
ITEMS_URL = "/api/v1/menu/items/"
GROUPS_URL = "/api/v1/menu/modifier-groups/"
OPTIONS_URL = "/api/v1/menu/modifier-options/"


@pytest.fixture
def owner(db):
    return User.objects.create_user(
        email="owner@example.com", password="StrongPass123!", first_name="Ow"
    )


@pytest.fixture
def stranger(db):
    return User.objects.create_user(
        email="stranger@example.com", password="StrongPass123!", first_name="St"
    )


@pytest.fixture
def restaurant(owner):
    return Restaurant.objects.create(name="Momo House", owner=owner)


@pytest.fixture
def category(restaurant):
    return Category.objects.create(restaurant=restaurant, name="Momos")


@pytest.fixture
def menu_setup(restaurant, category):
    group = ModifierGroup.objects.create(
        restaurant=restaurant, name="Size", min_select=1, max_select=1
    )
    small = ModifierOption.objects.create(group=group, name="Small", price_delta=0)
    large = ModifierOption.objects.create(group=group, name="Large", price_delta=60)
    veg = MenuItem.objects.create(
        category=category, name="Veg Momo", price=120, is_veg=True
    )
    veg.modifier_groups.add(group)
    nonveg = MenuItem.objects.create(
        category=category,
        name="Chicken Momo",
        price=180,
        compare_at_price=220,
        is_veg=False,
        is_available=False,
    )
    return {"group": group, "small": small, "large": large, "veg": veg, "nonveg": nonveg}


def _auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_public_can_browse_menu(menu_setup):
    assert APIClient().get(CATEGORIES_URL).status_code == 200
    response = APIClient().get(ITEMS_URL)
    assert response.status_code == 200
    assert response.data["count"] == 2


@pytest.mark.django_db
def test_anon_and_stranger_cannot_write(owner, stranger, restaurant):
    payload = {"restaurant": restaurant.id, "name": "Drinks"}
    assert APIClient().post(CATEGORIES_URL, payload, format="json").status_code in (
        401,
        403,
    )
    response = _auth_client(stranger).post(CATEGORIES_URL, payload, format="json")
    assert response.status_code == 403

    response = _auth_client(owner).post(CATEGORIES_URL, payload, format="json")
    assert response.status_code == 201, response.data
    assert response.data["slug"] == "drinks"


@pytest.mark.django_db
def test_category_slugs_unique_per_restaurant(owner, restaurant):
    client = _auth_client(owner)
    assert (
        client.post(
            CATEGORIES_URL, {"restaurant": restaurant.id, "name": "Momos"}, format="json"
        ).status_code
        == 201
    )
    response = client.post(
        CATEGORIES_URL, {"restaurant": restaurant.id, "name": "Momos"}, format="json"
    )
    assert response.status_code == 201
    assert response.data["slug"] == "momos-2"


@pytest.mark.django_db
def test_item_filters_and_search(owner, restaurant, category, menu_setup):
    client = APIClient()
    response = client.get(ITEMS_URL, {"restaurant": restaurant.id, "is_veg": "true"})
    assert response.status_code == 200
    assert [i["name"] for i in response.data["results"]] == ["Veg Momo"]

    response = client.get(ITEMS_URL, {"search": "chicken"})
    assert [i["name"] for i in response.data["results"]] == ["Chicken Momo"]

    response = client.get(ITEMS_URL, {"min_price": 150})
    assert [i["name"] for i in response.data["results"]] == ["Chicken Momo"]


@pytest.mark.django_db
def test_item_detail_nests_modifier_groups(menu_setup):
    veg_id = menu_setup["veg"].id
    response = APIClient().get(f"{ITEMS_URL}{veg_id}/")
    assert response.status_code == 200, response.data
    assert response.data["restaurant_id"] is not None
    groups = response.data["modifier_groups_detail"]
    assert len(groups) == 1 and groups[0]["name"] == "Size"
    assert {o["name"] for o in groups[0]["options"]} == {"Small", "Large"}


@pytest.mark.django_db
def test_item_validations(owner, category):
    client = _auth_client(owner)
    # compare_at_price below price is rejected.
    response = client.post(
        ITEMS_URL,
        {"category": category.id, "name": "Bad Deal", "price": 200, "compare_at_price": 150},
        format="json",
    )
    assert response.status_code == 400
    # negative price is rejected.
    response = client.post(
        ITEMS_URL, {"category": category.id, "name": "Neg", "price": -5}, format="json"
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_modifier_group_min_max_validation(owner, restaurant):
    response = _auth_client(owner).post(
        GROUPS_URL,
        {"restaurant": restaurant.id, "name": "Bad", "min_select": 3, "max_select": 1},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_available_manager_filters_unavailable(menu_setup):
    assert MenuItem.objects.count() == 2
    assert [i.name for i in MenuItem.objects.available()] == ["Veg Momo"]
    assert Category.objects.active().count() == 1


@pytest.mark.django_db
def test_stranger_cannot_delete_item(stranger, menu_setup):
    veg_id = menu_setup["veg"].id
    assert (
        _auth_client(stranger).delete(f"{ITEMS_URL}{veg_id}/").status_code == 403
    )
    assert MenuItem.objects.filter(pk=veg_id).exists()
