"""Cart tests: singleton per user, single-restaurant rule, modifier rules."""

from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.carts.models import CartItem
from apps.menu.models import Category, MenuItem, ModifierGroup, ModifierOption
from apps.restaurants.models import Restaurant

CART_URL = "/api/v1/cart/"
ITEMS_URL = "/api/v1/cart/items/"
CLEAR_URL = "/api/v1/cart/clear/"


@pytest.fixture
def owner(db):
    return User.objects.create_user(email="owner@example.com", password="StrongPass123!")


@pytest.fixture
def customer(db):
    return User.objects.create_user(
        email="customer@example.com", password="StrongPass123!"
    )


@pytest.fixture
def other_customer(db):
    return User.objects.create_user(email="other@example.com", password="StrongPass123!")


@pytest.fixture
def restaurant(owner):
    return Restaurant.objects.create(name="Momo House", owner=owner)


@pytest.fixture
def other_restaurant(owner):
    return Restaurant.objects.create(name="Pizza Place", owner=owner)


@pytest.fixture
def category(restaurant):
    return Category.objects.create(restaurant=restaurant, name="Momos")


@pytest.fixture
def shop(category, restaurant):
    """Item with a required Size group + a plain item + foreign option."""
    group = ModifierGroup.objects.create(
        restaurant=restaurant, name="Size", min_select=1, max_select=1
    )
    small = ModifierOption.objects.create(group=group, name="Small", price_delta=0)
    large = ModifierOption.objects.create(group=group, name="Large", price_delta=60)
    item = MenuItem.objects.create(category=category, name="Chicken Momo", price=180)
    item.modifier_groups.add(group)
    plain = MenuItem.objects.create(category=category, name="Fries", price=100)
    other_group = ModifierGroup.objects.create(restaurant=restaurant, name="Dip")
    foreign = ModifierOption.objects.create(group=other_group, name="Mayo", price_delta=20)
    return {
        "item": item,
        "plain": plain,
        "group": group,
        "small": small,
        "large": large,
        "foreign": foreign,
    }


def _auth(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_cart_starts_empty_and_requires_auth(customer):
    assert APIClient().get(CART_URL).status_code in (401, 403)
    response = _auth(customer).get(CART_URL)
    assert response.status_code == 200
    assert response.data["items"] == []
    assert Decimal(response.data["subtotal"]) == Decimal("0.00")


@pytest.mark.django_db
def test_add_item_with_modifier_and_totals(customer, shop):
    response = _auth(customer).post(
        ITEMS_URL,
        {
            "menu_item": shop["item"].id,
            "quantity": 2,
            "selected_options": [shop["large"].id],
        },
        format="json",
    )
    assert response.status_code == 200, response.data
    assert response.data["item_count"] == 2
    # (180 + 60) * 2
    assert Decimal(response.data["subtotal"]) == Decimal("480.00")
    line = response.data["items"][0]
    assert Decimal(line["unit_price"]) == Decimal("240.00")
    assert line["selected_options_detail"][0]["name"] == "Large"


@pytest.mark.django_db
def test_same_item_and_modifiers_merge(customer, shop):
    client = _auth(customer)
    payload = {"menu_item": shop["plain"].id, "quantity": 1}
    client.post(ITEMS_URL, payload, format="json")
    response = client.post(ITEMS_URL, payload, format="json")
    assert len(response.data["items"]) == 1
    assert response.data["items"][0]["quantity"] == 2


@pytest.mark.django_db
def test_same_item_different_modifiers_are_separate_lines(customer, shop):
    client = _auth(customer)
    base = {"menu_item": shop["item"].id, "quantity": 1}
    client.post(ITEMS_URL, {**base, "selected_options": [shop["small"].id]}, format="json")
    response = client.post(
        ITEMS_URL, {**base, "selected_options": [shop["large"].id]}, format="json"
    )
    assert len(response.data["items"]) == 2


@pytest.mark.django_db
def test_single_restaurant_rule_and_clear(customer, shop, other_restaurant, owner):
    client = _auth(customer)
    client.post(
        ITEMS_URL,
        {
            "menu_item": shop["item"].id,
            "quantity": 1,
            "selected_options": [shop["small"].id],
        },
        format="json",
    )
    other_category = Category.objects.create(
        restaurant=other_restaurant, name="Pizzas"
    )
    other_item = MenuItem.objects.create(
        category=other_category, name="Margherita", price=500
    )
    response = client.post(
        ITEMS_URL, {"menu_item": other_item.id, "quantity": 1}, format="json"
    )
    assert response.status_code == 400
    assert "another restaurant" in response.data["detail"]

    assert client.delete(CLEAR_URL).status_code == 200
    response = client.post(
        ITEMS_URL, {"menu_item": other_item.id, "quantity": 1}, format="json"
    )
    assert response.status_code == 200, response.data
    assert response.data["restaurant"] == other_restaurant.id


@pytest.mark.django_db
def test_required_modifier_group_enforced(customer, shop):
    response = _auth(customer).post(
        ITEMS_URL, {"menu_item": shop["item"].id, "quantity": 1}, format="json"
    )
    assert response.status_code == 400
    assert "Size" in str(response.data)


@pytest.mark.django_db
def test_foreign_modifier_option_rejected(customer, shop):
    response = _auth(customer).post(
        ITEMS_URL,
        {
            "menu_item": shop["plain"].id,
            "quantity": 1,
            "selected_options": [shop["foreign"].id],
        },
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_unavailable_item_rejected(customer, shop):
    shop["plain"].is_available = False
    shop["plain"].save(update_fields=["is_available"])
    response = _auth(customer).post(
        ITEMS_URL, {"menu_item": shop["plain"].id, "quantity": 1}, format="json"
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_patch_quantity_and_delete_resets_restaurant(customer, shop):
    client = _auth(customer)
    line_id = client.post(
        ITEMS_URL,
        {
            "menu_item": shop["item"].id,
            "quantity": 1,
            "selected_options": [shop["small"].id],
        },
        format="json",
    ).data["items"][0]["id"]

    response = client.patch(f"{ITEMS_URL}{line_id}/", {"quantity": 3}, format="json")
    assert response.status_code == 200
    assert response.data["quantity"] == 3

    assert client.patch(f"{ITEMS_URL}{line_id}/", {"quantity": 0}, format="json").status_code == 400

    cart = client.delete(f"{ITEMS_URL}{line_id}/").data
    assert cart["items"] == [] and cart["restaurant"] is None


@pytest.mark.django_db
def test_users_cannot_touch_each_others_lines(customer, other_customer, shop):
    line_id = (
        _auth(customer)
        .post(
            ITEMS_URL,
            {
                "menu_item": shop["item"].id,
                "quantity": 1,
                "selected_options": [shop["small"].id],
            },
            format="json",
        )
        .data["items"][0]["id"]
    )
    stranger = _auth(other_customer)
    assert stranger.patch(f"{ITEMS_URL}{line_id}/", {"quantity": 5}, format="json").status_code == 404
    assert stranger.delete(f"{ITEMS_URL}{line_id}/").status_code == 404
    assert CartItem.objects.filter(pk=line_id).exists()
