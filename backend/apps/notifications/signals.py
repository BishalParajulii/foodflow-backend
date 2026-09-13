"""Order signals: turn lifecycle events into user notifications."""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.notifications.models import Notification, NotificationType
from apps.orders.models import Order, OrderStatus

STATUS_LABELS = {
    OrderStatus.CONFIRMED: "confirmed",
    OrderStatus.PREPARING: "being prepared",
    OrderStatus.READY: "ready",
    OrderStatus.OUT_FOR_DELIVERY: "out for delivery",
    OrderStatus.DELIVERED: "delivered",
}


@receiver(pre_save, sender=Order)
def _stash_old_status(sender, instance, **kwargs):
    if instance.pk:
        old = sender.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
        instance._pre_save_status = old
    else:
        instance._pre_save_status = None


@receiver(post_save, sender=Order)
def _notify_order_event(sender, instance, created, **kwargs):
    restaurant_name = (
        instance.restaurant.name if instance.restaurant_id else "restaurant"
    )
    if created:
        Notification.objects.create(
            user=instance.user,
            type=NotificationType.ORDER_PLACED,
            title=f"Order placed at {restaurant_name}",
            body=(
                f"Your order (Rs. {instance.total}) is pending confirmation. "
                "Pay in cash on delivery."
            ),
            order=instance,
        )
        owner_id = instance.restaurant.owner_id if instance.restaurant_id else None
        if owner_id and owner_id != instance.user_id:
            Notification.objects.create(
                user_id=owner_id,
                type=NotificationType.ORDER_PLACED,
                title="New order received",
                body=f"New pending order (Rs. {instance.total}) at {restaurant_name}.",
                order=instance,
            )
        return

    old_status = getattr(instance, "_pre_save_status", None)
    if not old_status or old_status == instance.status:
        return
    if instance.status == OrderStatus.CANCELLED:
        Notification.objects.create(
            user=instance.user,
            type=NotificationType.ORDER_CANCELLED,
            title=f"Order cancelled ({restaurant_name})",
            body="Your order was cancelled.",
            order=instance,
        )
    elif instance.status in STATUS_LABELS:
        Notification.objects.create(
            user=instance.user,
            type=NotificationType.ORDER_STATUS,
            title=f"Order update: {STATUS_LABELS[instance.status]}",
            body=f"Your order at {restaurant_name} is {STATUS_LABELS[instance.status]}.",
            order=instance,
        )
