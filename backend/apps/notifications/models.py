"""User notifications: order lifecycle events, inbox-style."""

from django.conf import settings
from django.db import models

from apps.common.models import BaseModel
from apps.orders.models import Order


class NotificationType(models.TextChoices):
    ORDER_PLACED = "order_placed", "Order placed"
    ORDER_STATUS = "order_status", "Order status update"
    ORDER_CANCELLED = "order_cancelled", "Order cancelled"
    GENERAL = "general", "General"


class Notification(BaseModel):
    """An inbox entry for a user. Created server-side (see signals)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.CharField(
        max_length=20, choices=NotificationType.choices, default=NotificationType.GENERAL
    )
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True, default="")
    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"Notification ({self.type}) for {self.user_id}"
