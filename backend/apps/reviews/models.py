"""Restaurant reviews: verified (delivered order) or open ratings."""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import BaseModel
from apps.orders.models import Order
from apps.restaurants.models import Restaurant


class Review(BaseModel):
    """A 1–5 star rating + optional comment for a restaurant.

    Linked to a delivered order when possible (verified purchase);
    otherwise an open review. One review per order; one open review
    per (user, restaurant) — enforced in the serializer.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="reviews"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviews",
        help_text="Delivered order this review is based on (verified purchase).",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, blank=True, default="")
    comment = models.TextField(blank=True, default="")
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["restaurant", "-created_at"]),
            models.Index(fields=["restaurant", "rating"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["order"],
                condition=models.Q(order__isnull=False),
                name="uniq_review_per_order",
            )
        ]

    def __str__(self) -> str:
        return f"Review {self.rating}/5 for {self.restaurant_id} by {self.user_id}"
