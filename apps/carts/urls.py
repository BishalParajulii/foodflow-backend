"""Cart URL namespace: /api/v1/cart/ (authenticated users only)."""

from django.urls import path

from apps.carts.views import (
    CartClearView,
    CartDetailView,
    CartItemCreateView,
    CartItemDetailView,
)

app_name = "carts"

urlpatterns = [
    path("", CartDetailView.as_view(), name="detail"),
    path("items/", CartItemCreateView.as_view(), name="item-add"),
    path("items/<int:pk>/", CartItemDetailView.as_view(), name="item-detail"),
    path("clear/", CartClearView.as_view(), name="clear"),
]
