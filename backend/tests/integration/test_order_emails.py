"""Order email tests: Celery tasks queue on checkout and status changes.

Runs tasks eagerly (CELERY_TASK_ALWAYS_EAGER in test settings) and asserts on
django.core.mail.outbox (locmem backend). transaction.on_commit callbacks are
captured and executed when the django_capture_on_commit_callbacks block exits.
"""

import uuid

import pytest
from django.core import mail
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.menu.models import Category, MenuItem
from apps.orders.models import Order
from apps.orders.tasks import (
    send_new_order_email,
    send_order_confirmation_email,
    send_order_status_email,
)
from apps.restaurants.models import Restaurant

ORDERS_URL = "/api/v1/orders/"
CART_ITEMS_URL = "/api/v1/cart/items/"


@pytest.fixture(autouse=True)
def _clear_outbox():
    mail.outbox.clear()
    yield
    mail.outbox.clear()


@pytest.fixture
def owner(db):
    return User.objects.create_user(email="owner@example.com", password="StrongPass123!")


@pytest.fixture
def customer(db):
    return User.objects.create_user(email="customer@example.com", password="StrongPass123!")


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


def _place_order(customer, shop, address="Thamel 12"):
    client = _auth(customer)
    added = client.post(
        CART_ITEMS_URL,
        {"menu_item": str(shop["item"].id), "quantity": 2},
        format="json",
    )
    assert added.status_code == 200, added.data
    response = client.post(
        ORDERS_URL, {"delivery_address": address, "phone": "+9779800000001"}, format="json"
    )
    assert response.status_code == 201, response.data
    return response.data["data"]


@pytest.mark.django_db
def test_checkout_mails_customer_and_owner(
    customer, owner, shop, django_capture_on_commit_callbacks
):
    with django_capture_on_commit_callbacks(execute=True):
        order = _place_order(customer, shop)

    assert len(mail.outbox) == 2
    to_customer = [m for m in mail.outbox if customer.email in m.to]
    to_owner = [m for m in mail.outbox if owner.email in m.to]
    assert len(to_customer) == 1 and len(to_owner) == 1

    confirmation = to_customer[0]
    assert "Momo House" in confirmation.subject
    assert "Chicken Momo" in confirmation.body
    assert "Thamel 12" in confirmation.body
    # HTML alternative attached.
    html_parts = [
        content for content, mimetype in confirmation.alternatives if mimetype == "text/html"
    ]
    assert html_parts and "Chicken Momo" in html_parts[0]

    new_order = to_owner[0]
    assert "New order" in new_order.subject
    assert str(order["id"]) in new_order.body


@pytest.mark.django_db
def test_status_change_mails_customer(customer, owner, shop, django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        order = _place_order(customer, shop)
    mail.outbox.clear()

    with django_capture_on_commit_callbacks(execute=True):
        client = _auth(owner)
        patched = client.patch(
            f"{ORDERS_URL}{order['id']}/", {"status": "confirmed"}, format="json"
        )
        assert patched.status_code == 200, patched.data

    assert len(mail.outbox) == 1
    message = mail.outbox[0]
    assert customer.email in message.to
    assert "confirmed" in message.subject
    assert owner.email not in message.to


@pytest.mark.django_db
def test_cancel_mails_customer(customer, owner, shop, django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        order = _place_order(customer, shop)
    mail.outbox.clear()

    with django_capture_on_commit_callbacks(execute=True):
        client = _auth(customer)
        cancelled = client.post(f"{ORDERS_URL}{order['id']}/cancel/", format="json")
        assert cancelled.status_code == 200, cancelled.data

    assert len(mail.outbox) == 1
    assert "cancelled" in mail.outbox[0].subject


@pytest.mark.django_db
def test_unchanged_status_mails_nothing(customer, owner, shop, django_capture_on_commit_callbacks):
    with django_capture_on_commit_callbacks(execute=True):
        order = _place_order(customer, shop)
    mail.outbox.clear()

    with django_capture_on_commit_callbacks(execute=True):
        client = _auth(owner)
        # Same status is accepted but must not re-send anything.
        patched = client.patch(
            f"{ORDERS_URL}{order['id']}/", {"status": "pending"}, format="json"
        )
        assert patched.status_code == 200, patched.data

    assert mail.outbox == []


@pytest.mark.django_db
def test_ordering_own_restaurant_skips_owner_email(shop, django_capture_on_commit_callbacks):
    """Owner is both customer and shop owner: only the confirmation goes out."""
    self_customer = shop["restaurant"].owner
    with django_capture_on_commit_callbacks(execute=True):
        _place_order(self_customer, shop)

    assert len(mail.outbox) == 1
    assert self_customer.email in mail.outbox[0].to


@pytest.mark.django_db
def test_tasks_noop_on_missing_order(db):
    missing = str(uuid.uuid4())
    send_order_confirmation_email.delay(missing)
    send_new_order_email.delay(missing)
    send_order_status_email.delay(missing, "confirmed")
    assert mail.outbox == []


@pytest.mark.django_db
def test_status_task_prefers_explicit_status_over_db(customer, owner, shop):
    """Back-to-back changes: the task mails the transition it was asked for,
    not whatever state the order happens to be in when the worker runs."""
    order = _place_order(customer, shop)
    Order.objects.filter(pk=order["id"]).update(status="confirmed")

    send_order_status_email.delay(str(order["id"]), "preparing")

    assert len(mail.outbox) == 1
    assert "being prepared" in mail.outbox[0].subject
    assert "confirmed" not in mail.outbox[0].subject