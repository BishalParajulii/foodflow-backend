"""Notification tests: auto-created on order events, private inbox, read flow."""

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.menu.models import Category, MenuItem
from apps.notifications.models import Notification
from apps.restaurants.models import Restaurant

NOTIFS_URL = "/api/v1/notifications/"
ORDERS_URL = "/api/v1/orders/"
CART_ITEMS_URL = "/api/v1/cart/items/"


@pytest.fixture
def owner(db):
    return User.objects.create_user(email="owner@example.com", password="StrongPass123!")


@pytest.fixture
def customer(db):
    return User.objects.create_user(email="customer@example.com", password="StrongPass123!")


@pytest.fixture
def stranger(db):
    return User.objects.create_user(email="stranger@example.com", password="StrongPass123!")


@pytest.fixture
def shop(owner):
    restaurant = Restaurant.objects.create(name="Momo House", owner=owner)
    category = Category.objects.create(restaurant=restaurant, name="Momos")
    item = MenuItem.objects.create(category=category, name="Chicken Momo", price=180)
    return {"restaurant": restaurant, "item": item}


def _auth(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def _place_order(customer, shop):
    client = _auth(customer)
    add = client.post(
        CART_ITEMS_URL, {"menu_item": str(shop["item"].id), "quantity": 1}, format="json"
    )
    assert add.status_code == 200, add.data
    response = client.post(
        ORDERS_URL, {"delivery_address": "Thamel", "phone": "+9779800000001"}, format="json"
    )
    assert response.status_code == 201, response.data
    return response.data["data"]


@pytest.mark.django_db
def test_notifications_require_auth():
    assert APIClient().get(NOTIFS_URL).status_code in (401, 403)


@pytest.mark.django_db
def test_checkout_notifies_customer_and_owner(customer, owner, shop):
    order = _place_order(customer, shop)
    mine = Notification.objects.filter(user=customer).order_by("created_at")
    assert mine.count() == 1
    assert mine[0].type == "order_placed"
    assert mine[0].order_id is not None
    assert str(mine[0].order_id) == order["id"]
    owners = Notification.objects.filter(user=owner)
    assert owners.count() == 1
    assert owners[0].title == "New order received"


@pytest.mark.django_db
def test_status_change_and_cancel_notify_customer(customer, owner, shop):
    order = _place_order(customer, shop)
    staff = _auth(owner)
    confirmed = staff.patch(
        ORDERS_URL + f"{order['id']}/", {"status": "confirmed"}, format="json"
    )
    preparing = staff.patch(
        ORDERS_URL + f"{order['id']}/", {"status": "preparing"}, format="json"
    )
    cancelled = staff.post(ORDERS_URL + f"{order['id']}/cancel/", {}, format="json")
    assert confirmed.status_code == 200
    assert preparing.status_code == 200
    assert cancelled.status_code == 200

    types = list(
        Notification.objects.filter(user=customer)
        .order_by("created_at")
        .values_list("type", flat=True)
    )
    assert types == ["order_placed", "order_status", "order_status", "order_cancelled"]


@pytest.mark.django_db
def test_inbox_scoped_and_read_flow(customer, stranger, shop):
    _place_order(customer, shop)
    mine = _auth(customer).get(NOTIFS_URL)
    assert mine.status_code == 200, mine.data
    assert mine.data["data"]["count"] == 1
    assert _auth(stranger).get(NOTIFS_URL).data["data"]["count"] == 0

    notif_id = mine.data["data"]["results"][0]["id"]
    # Title is read-only: attempts to change it are ignored.
    patched = _auth(customer).patch(
        f"{NOTIFS_URL}{notif_id}/", {"is_read": True, "title": "Hacked"}, format="json"
    )
    assert patched.status_code == 200, patched.data
    assert patched.data["data"]["is_read"] is True
    assert patched.data["data"]["title"] != "Hacked"

    count = _auth(customer).get(NOTIFS_URL + "unread-count/")
    assert count.data["data"]["unread_count"] == 0

    # Stranger cannot touch someone else's notification.
    forbidden = _auth(stranger).patch(
        f"{NOTIFS_URL}{notif_id}/", {"is_read": True}, format="json"
    )
    assert forbidden.status_code == 404


@pytest.mark.django_db
def test_mark_all_read(customer, owner, shop):
    order = _place_order(customer, shop)
    _auth(owner).patch(ORDERS_URL + f"{order['id']}/", {"status": "confirmed"}, format="json")
    client = _auth(customer)
    response = client.post(NOTIFS_URL + "mark-all-read/", {}, format="json")
    assert response.status_code == 200, response.data
    assert response.data["data"]["updated"] == 2
    assert client.get(NOTIFS_URL + "unread-count/").data["data"]["unread_count"] == 0
