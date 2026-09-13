"""Review tests: public browse, verified-purchase rules, ownership, summary."""

from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.orders.models import Order, OrderStatus
from apps.restaurants.models import Restaurant
from apps.reviews.models import Review

REVIEWS_URL = "/api/v1/reviews/"
SUMMARY_URL = "/api/v1/reviews/summary/"


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
def restaurant(owner):
    return Restaurant.objects.create(name="Momo House", owner=owner)


def _auth(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def _order(user, restaurant, status=OrderStatus.DELIVERED):
    return Order.objects.create(
        user=user,
        restaurant=restaurant,
        status=status,
        subtotal=Decimal("100.00"),
        delivery_fee=Decimal("0.00"),
        total=Decimal("100.00"),
    )


def _review_payload(restaurant, **overrides):
    payload = {"restaurant": str(restaurant.id), "rating": 5, "comment": "Great!"}
    payload.update(overrides)
    return payload


@pytest.mark.django_db
def test_reviews_list_is_public_but_create_needs_auth(restaurant):
    assert APIClient().get(REVIEWS_URL).status_code == 200
    response = APIClient().post(REVIEWS_URL, _review_payload(restaurant), format="json")
    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_create_open_review(customer, restaurant):
    response = _auth(customer).post(REVIEWS_URL, _review_payload(restaurant), format="json")
    assert response.status_code == 201, response.data
    data = response.data["data"]
    assert data["rating"] == 5
    assert data["user_email"] == "customer@example.com"
    assert data["restaurant_name"] == "Momo House"


@pytest.mark.django_db
def test_rating_must_be_1_to_5(customer, restaurant):
    client = _auth(customer)
    bad_low = client.post(REVIEWS_URL, _review_payload(restaurant, rating=0), format="json")
    bad_high = client.post(REVIEWS_URL, _review_payload(restaurant, rating=6), format="json")
    assert bad_low.status_code == 400
    assert bad_high.status_code == 400


@pytest.mark.django_db
def test_duplicate_open_review_rejected(customer, restaurant):
    client = _auth(customer)
    assert client.post(REVIEWS_URL, _review_payload(restaurant), format="json").status_code == 201
    response = client.post(REVIEWS_URL, _review_payload(restaurant, rating=4), format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_verified_review_needs_delivered_own_order(customer, stranger, restaurant, owner):
    other_restaurant = Restaurant.objects.create(name="Other Place", owner=owner)
    own_pending = _order(customer, restaurant, status=OrderStatus.PENDING)
    own_delivered = _order(customer, restaurant)
    strangers = _order(stranger, restaurant)

    client = _auth(customer)
    # Pending order -> rejected.
    response = client.post(
        REVIEWS_URL,
        _review_payload(restaurant, order=str(own_pending.id)),
        format="json",
    )
    assert response.status_code == 400
    # Someone else's order -> rejected.
    response = client.post(
        REVIEWS_URL, _review_payload(restaurant, order=str(strangers.id)), format="json"
    )
    assert response.status_code == 400
    # Order from another restaurant -> rejected.
    response = client.post(
        REVIEWS_URL,
        _review_payload(other_restaurant, order=str(own_delivered.id)),
        format="json",
    )
    assert response.status_code == 400
    # Delivered own order -> accepted.
    response = client.post(
        REVIEWS_URL, _review_payload(restaurant, order=str(own_delivered.id)), format="json"
    )
    assert response.status_code == 201, response.data
    # Same order twice -> rejected.
    response = client.post(
        REVIEWS_URL,
        _review_payload(restaurant, rating=4, order=str(own_delivered.id)),
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_only_author_or_admin_can_edit(customer, stranger, restaurant):
    review = Review.objects.create(user=customer, restaurant=restaurant, rating=4)
    url = f"{REVIEWS_URL}{review.id}/"
    assert APIClient().patch(url, {"rating": 1}, format="json").status_code in (401, 403)
    assert _auth(stranger).patch(url, {"rating": 1}, format="json").status_code == 403
    response = _auth(customer).patch(url, {"rating": 2}, format="json")
    assert response.status_code == 200, response.data
    assert response.data["data"]["rating"] == 2


@pytest.mark.django_db
def test_filter_by_restaurant_and_rating(customer, stranger, restaurant, owner):
    other = Restaurant.objects.create(name="Other Place", owner=owner)
    Review.objects.create(user=customer, restaurant=restaurant, rating=5)
    Review.objects.create(user=stranger, restaurant=restaurant, rating=2)
    Review.objects.create(user=customer, restaurant=other, rating=5)

    client = APIClient()
    by_restaurant = client.get(REVIEWS_URL, {"restaurant": str(restaurant.id)}).data["data"]
    by_rating = client.get(REVIEWS_URL, {"rating": 5}).data["data"]
    assert by_restaurant["count"] == 2
    assert by_rating["count"] == 2


@pytest.mark.django_db
def test_summary_and_restaurant_rating_fields(customer, stranger, restaurant):
    Review.objects.create(user=customer, restaurant=restaurant, rating=5)
    Review.objects.create(user=stranger, restaurant=restaurant, rating=3)

    summary = APIClient().get(SUMMARY_URL, {"restaurant": str(restaurant.id)})
    assert summary.status_code == 200, summary.data
    assert summary.data["data"]["average_rating"] == 4.0
    assert summary.data["data"]["review_count"] == 2

    detail = APIClient().get(f"/api/v1/restaurants/{restaurant.id}/")
    assert detail.status_code == 200, detail.data
    assert detail.data["data"]["rating_average"] == 4.0
    assert detail.data["data"]["review_count"] == 2
