"""Order tests: checkout snapshot, history scoping, status lifecycle."""

from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.menu.models import Category, MenuItem, ModifierGroup, ModifierOption
from apps.orders.models import Order
from apps.restaurants.models import Restaurant

ORDERS_URL = "/api/v1/orders/"
CART_ITEMS_URL = "/api/v1/cart/items/"
CART_URL = "/api/v1/cart/"


@pytest.fixture
def owner(db):
    return User.objects.create_user(email="owner@example.com", password="StrongPass123!")


@pytest.fixture
def customer(db):
    return User.objects.create_user(
        email="customer@example.com", password="StrongPass123!"
    )


@pytest.fixture
def stranger(db):
    return User.objects.create_user(
        email="stranger@example.com", password="StrongPass123!"
    )


@pytest.fixture
def admin(db):
    user = User.objects.create_user(email="admin@example.com", password="StrongPass123!")
    user.is_staff = True
    user.is_superuser = True
    user.save(update_fields=["is_staff", "is_superuser"])
    return user


@pytest.fixture
def restaurant(owner):
    return Restaurant.objects.create(name="Momo House", owner=owner)


@pytest.fixture
def category(restaurant):
    return Category.objects.create(restaurant=restaurant, name="Momos")


@pytest.fixture
def shop(category, restaurant):
    group = ModifierGroup.objects.create(
        restaurant=restaurant, name="Size", min_select=1, max_select=1
    )
    small = ModifierOption.objects.create(group=group, name="Small", price_delta=0)
    large = ModifierOption.objects.create(group=group, name="Large", price_delta=60)
    item = MenuItem.objects.create(category=category, name="Chicken Momo", price=180)
    item.modifier_groups.add(group)
    plain = MenuItem.objects.create(category=category, name="Fries", price=100)
    return {"item": item, "plain": plain, "group": group, "small": small, "large": large}


def _auth(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def _add(client, menu_item, quantity=1, options=None):
    payload = {"menu_item": str(menu_item.id), "quantity": quantity}
    if options:
        payload["selected_options"] = [str(o.id) for o in options]
    return client.post(CART_ITEMS_URL, payload, format="json")


def _checkout(client, **kwargs):
    return client.post(ORDERS_URL, kwargs, format="json")


@pytest.mark.django_db
def test_orders_require_auth():
    assert APIClient().get(ORDERS_URL).status_code in (401, 403)
    assert APIClient().post(ORDERS_URL, {}, format="json").status_code in (401, 403)


@pytest.mark.django_db
def test_checkout_empty_cart_returns_400(customer):
    response = _checkout(_auth(customer))
    assert response.status_code == 400
    assert response.data["error"]["code"] == "empty_cart"


@pytest.mark.django_db
def test_checkout_freezes_prices_and_clears_cart(customer, shop, restaurant):
    client = _auth(customer)
    assert _add(client, shop["item"], quantity=2, options=[shop["large"]]).status_code == 200
    assert _add(client, shop["plain"], quantity=1).status_code == 200

    response = _checkout(
        client, delivery_address="Thamel", phone="+9779800000001", notes="extra spicy"
    )
    assert response.status_code == 201, response.data
    data = response.data["data"]
    assert data["status"] == "pending"
    assert str(data["restaurant"]) == str(restaurant.id)
    assert data["delivery_address"] == "Thamel"
    assert data["item_count"] == 3
    # (180 + 60) * 2 + 100
    assert Decimal(data["subtotal"]) == Decimal("580.00")
    assert Decimal(data["total"]) == Decimal("580.00")
    assert len(data["items"]) == 2
    momo_line = next(i for i in data["items"] if i["menu_item_name"] == "Chicken Momo")
    assert Decimal(momo_line["unit_price"]) == Decimal("240.00")
    assert Decimal(momo_line["line_total"]) == Decimal("480.00")
    assert momo_line["selected_options_detail"][0]["name"] == "Large"

    # Cart is emptied and unlocked.
    cart = client.get(CART_URL).data["data"]
    assert cart["items"] == [] and cart["restaurant"] is None

    # Later menu edits never rewrite the frozen order.
    shop["item"].price = Decimal("999.00")
    shop["item"].save(update_fields=["price"])
    order = Order.objects.get(pk=data["id"])
    assert order.subtotal == Decimal("580.00")
    assert order.total == Decimal("580.00")


@pytest.mark.django_db
def test_checkout_rejects_stale_unavailable_item(customer, shop):
    client = _auth(customer)
    assert _add(client, shop["plain"]).status_code == 200
    shop["plain"].is_available = False
    shop["plain"].save(update_fields=["is_available"])
    response = _checkout(client)
    assert response.status_code == 400


@pytest.mark.django_db
def test_order_list_scoping(customer, stranger, owner, admin, shop, restaurant):
    _add(_auth(customer), shop["plain"])
    order_id = _checkout(_auth(customer)).data["data"]["id"]

    # Mine.
    assert _auth(customer).get(ORDERS_URL).data["data"]["count"] == 1
    # Stranger sees none; direct access does not leak (404).
    assert _auth(stranger).get(ORDERS_URL).data["data"]["count"] == 0
    assert _auth(stranger).get(f"{ORDERS_URL}{order_id}/").status_code == 404
    # Restaurant owner sees their restaurant's orders.
    assert _auth(owner).get(ORDERS_URL).data["data"]["count"] == 1
    assert _auth(owner).get(f"{ORDERS_URL}{order_id}/").status_code == 200
    # Admin sees all.
    assert _auth(admin).get(ORDERS_URL).data["data"]["count"] == 1


@pytest.mark.django_db
def test_customer_cannot_self_confirm(customer, shop):
    client = _auth(customer)
    _add(client, shop["plain"])
    order_id = _checkout(client).data["data"]["id"]
    response = client.patch(f"{ORDERS_URL}{order_id}/", {"status": "confirmed"}, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_restaurant_owner_lifecycle(customer, owner, shop):
    customer_client, owner_client = _auth(customer), _auth(owner)
    _add(customer_client, shop["plain"])
    order_id = _checkout(customer_client).data["data"]["id"]
    url = f"{ORDERS_URL}{order_id}/"

    # Invalid jump is rejected.
    response = owner_client.patch(url, {"status": "preparing"}, format="json")
    assert response.status_code == 400

    lifecycle = ["confirmed", "preparing", "ready", "out_for_delivery", "delivered"]
    for next_status in lifecycle:
        response = owner_client.patch(url, {"status": next_status}, format="json")
        assert response.status_code == 200, (next_status, response.data)
        assert response.data["data"]["status"] == next_status

    # Terminal: no further moves.
    assert owner_client.patch(url, {"status": "cancelled"}, format="json").status_code == 400


@pytest.mark.django_db
def test_customer_cancel_flow(customer, owner, shop):
    customer_client, owner_client = _auth(customer), _auth(owner)
    _add(customer_client, shop["plain"])
    order_id = _checkout(customer_client).data["data"]["id"]

    # Customer cancels a pending order (cancel shortcut).
    response = customer_client.post(f"{ORDERS_URL}{order_id}/cancel/")
    assert response.status_code == 200
    assert response.data["data"]["status"] == "cancelled"

    # Second order: owner confirms, then customer cancel is rejected.
    _add(customer_client, shop["plain"])
    order_id = _checkout(customer_client).data["data"]["id"]
    url = f"{ORDERS_URL}{order_id}/"
    assert owner_client.patch(url, {"status": "confirmed"}, format="json").status_code == 200
    assert owner_client.patch(url, {"status": "preparing"}, format="json").status_code == 200
    response = customer_client.post(f"{ORDERS_URL}{order_id}/cancel/")
    assert response.status_code == 400


@pytest.mark.django_db
def test_owner_can_cancel_pending(customer, owner, shop):
    _add(_auth(customer), shop["plain"])
    order_id = _checkout(_auth(customer)).data["data"]["id"]
    response = _auth(owner).post(f"{ORDERS_URL}{order_id}/cancel/")
    assert response.status_code == 200
    assert response.data["data"]["status"] == "cancelled"


@pytest.mark.django_db
def test_status_patch_validates_payload(customer, shop):
    client = _auth(customer)
    _add(client, shop["plain"])
    order_id = _checkout(client).data["data"]["id"]
    url = f"{ORDERS_URL}{order_id}/"
    assert client.patch(url, {}, format="json").status_code == 400
    payload = {"status": "confirmed", "notes": "x"}
    assert client.patch(url, payload, format="json").status_code == 400
    assert client.patch(url, {"status": "nope"}, format="json").status_code == 400


@pytest.mark.django_db
def test_orders_are_not_deletable_or_replaceable(customer, shop):
    client = _auth(customer)
    _add(client, shop["plain"])
    order_id = _checkout(client).data["data"]["id"]
    url = f"{ORDERS_URL}{order_id}/"
    assert client.put(url, {"status": "confirmed"}, format="json").status_code == 405
    assert client.delete(url).status_code == 405


@pytest.mark.django_db
def test_order_filters(customer, shop, restaurant):
    client = _auth(customer)
    _add(client, shop["plain"])
    order_id = _checkout(client).data["data"]["id"]
    assert client.get(f"{ORDERS_URL}?status=pending").data["data"]["count"] == 1
    assert client.get(f"{ORDERS_URL}?status=delivered").data["data"]["count"] == 0
    assert client.get(f"{ORDERS_URL}?restaurant={restaurant.id}").data["data"]["count"] == 1
    assert client.get(f"{ORDERS_URL}{order_id}/").data["data"]["id"] == order_id
