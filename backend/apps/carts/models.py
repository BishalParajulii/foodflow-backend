"""Cart models: one active cart per user, single-restaurant rule.

A cart holds ephemeral lines priced live off the menu. Checkout (orders app)
will snapshot lines into an order; prices are frozen there, not here.
"""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import BaseModel
from apps.menu.models import ModifierOption
from apps.restaurants.models import Restaurant

MAX_QUANTITY = 99


class Cart(BaseModel):
    """The active cart of a user (created on demand)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="carts",
        help_text="Locked to the first item's restaurant; cleared with the cart.",
    )

    def __str__(self) -> str:
        return f"Cart of {self.user}"

    @property
    def item_count(self) -> int:
        return sum(line.quantity for line in self.items.all())

    @property
    def subtotal(self) -> Decimal:
        total = Decimal("0.00")
        for line in self.items.select_related("menu_item").prefetch_related(
            "selected_options"
        ):
            total += line.line_total
        return total.quantize(Decimal("0.00"))

    def find_line(self, menu_item, option_ids: set[int]):
        """Return the line with the same item + exact modifier set, if any."""
        for line in self.items.prefetch_related("selected_options"):
            if line.menu_item_id == menu_item.id and {
                o.id for o in line.selected_options.all()
            } == set(option_ids):
                return line
        return None

    def reset_restaurant_if_empty(self):
        if not self.items.exists() and self.restaurant_id is not None:
            self.restaurant = None
            self.save(update_fields=["restaurant", "updated_at"])


class CartItem(BaseModel):
    """One line in a cart: item + quantity + chosen modifier options."""

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(
        "menu.MenuItem", on_delete=models.CASCADE, related_name="cart_lines"
    )
    quantity = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(MAX_QUANTITY)]
    )
    selected_options = models.ManyToManyField(
        ModifierOption, blank=True, related_name="cart_lines"
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.quantity} x {self.menu_item.name}"

    @property
    def unit_price(self) -> Decimal:
        extras = sum(
            (o.price_delta for o in self.selected_options.all()), Decimal("0.00")
        )
        return (self.menu_item.price + extras).quantize(Decimal("0.00"))

    @property
    def line_total(self) -> Decimal:
        return (self.unit_price * self.quantity).quantize(Decimal("0.00"))
