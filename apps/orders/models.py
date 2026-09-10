"""Order models: checkout snapshot + lifecycle state machine.

Flow: cart (live prices) -> checkout -> order (frozen prices).
An order locks to one restaurant (same rule as the cart). Prices and modifier
choices are snapshotted so later menu edits never rewrite history.
"""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import BaseModel
from apps.menu.models import ModifierOption
from apps.restaurants.models import Restaurant

MAX_QUANTITY = 99


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    PREPARING = "preparing", "Preparing"
    READY = "ready", "Ready"
    OUT_FOR_DELIVERY = "out_for_delivery", "Out for delivery"
    DELIVERED = "delivered", "Delivered"
    CANCELLED = "cancelled", "Cancelled"


#: Allowed forward moves (cancel is terminal alongside delivered).
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.PREPARING, OrderStatus.CANCELLED},
    OrderStatus.PREPARING: {OrderStatus.READY, OrderStatus.CANCELLED},
    OrderStatus.READY: {OrderStatus.OUT_FOR_DELIVERY},
    OrderStatus.OUT_FOR_DELIVERY: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set(),
}

#: Customer (order owner) may only cancel, and only before preparation.
CUSTOMER_CANCELLABLE_FROM = {OrderStatus.PENDING, OrderStatus.CONFIRMED}


class OrderQuerySet(models.QuerySet):
    def for_user(self, user):
        """Orders visible to ``user``: own + owned-restaurant + staff-all."""
        from apps.restaurants.permissions import is_platform_admin

        if is_platform_admin(user):
            return self.all()
        owned = models.Q(restaurant__owner=user)
        return self.filter(models.Q(user=user) | owned).distinct()


class Order(BaseModel):
    """A placed order: frozen totals + status lifecycle."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.PROTECT, related_name="orders"
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        db_index=True,
    )
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    delivery_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    delivery_address = models.CharField(max_length=255, blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    notes = models.TextField(blank=True, default="")

    objects = OrderQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order {self.id} ({self.status})"

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items.all())

    def can_transition_to(self, new_status: str) -> bool:
        return new_status in ALLOWED_TRANSITIONS.get(self.status, set())


class OrderItem(BaseModel):
    """One frozen line of an order (prices snapshot at checkout)."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(
        "menu.MenuItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_lines",
        help_text="Kept for reference; display name/price are snapshotted.",
    )
    menu_item_name = models.CharField(max_length=200, default="")
    quantity = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(MAX_QUANTITY)]
    )
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    line_total = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    selected_options = models.ManyToManyField(
        ModifierOption, blank=True, related_name="order_lines"
    )
    selected_options_snapshot = models.JSONField(
        default=list,
        blank=True,
        help_text="Frozen [{id, name, price_delta, group, group_name}].",
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.quantity} x {self.menu_item_name}"
