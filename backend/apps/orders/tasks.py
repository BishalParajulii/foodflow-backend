"""Order lifecycle emails, sent asynchronously through Celery.

Tasks look the order up by id so they stay safe across broker round-trips
(no model instances in the task payload). Missing orders (deleted before the
worker ran) log and no-op instead of raising.
"""

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from apps.orders.models import Order, OrderStatus

logger = logging.getLogger(__name__)

#: Customer-facing labels for every lifecycle state.
STATUS_LABELS: dict[str, str] = {
    OrderStatus.PENDING: "pending confirmation",
    OrderStatus.CONFIRMED: "confirmed",
    OrderStatus.PREPARING: "being prepared",
    OrderStatus.READY: "ready",
    OrderStatus.OUT_FOR_DELIVERY: "out for delivery",
    OrderStatus.DELIVERED: "delivered",
    OrderStatus.CANCELLED: "cancelled",
}


def _get_order(order_id: str) -> Order | None:
    try:
        return (
            Order.objects.select_related("user", "restaurant", "restaurant__owner")
            .prefetch_related("items")
            .get(pk=order_id)
        )
    except (Order.DoesNotExist, ValueError, TypeError):
        logger.warning("Order email task: order %s not found (skipped)", order_id)
        return None


def _order_lines_html(order: Order) -> str:
    rows = "\n".join(
        f'<tr><td>{item.quantity} x {item.menu_item_name or "Item"}</td>'
        f"<td style='text-align:right'>Rs. {item.line_total}</td></tr>"
        for item in order.items.all()
    )
    return (
        f"<table cellpadding='4' cellspacing='0' width='100%'>"
        f"<tr style='border-bottom:1px solid #ddd'><th align='left'>Item</th>"
        f"<th align='right'>Amount</th></tr>{rows}</table>"
    )


def _summary_html(order: Order) -> str:
    address = ""
    if order.delivery_address:
        address = f"<p><strong>Deliver to:</strong> {order.delivery_address}</p>"
    return (
        f"<p>Hi {order.user.get_short_name()},</p>"
        f"<p>Order <strong>{order.pk}</strong> at "
        f"<strong>{order.restaurant.name if order.restaurant_id else 'FoodFlow'}</strong>:</p>"
        f"{_order_lines_html(order)}"
        f"<p>Subtotal: Rs. {order.subtotal}<br>"
        f"Delivery fee: Rs. {order.delivery_fee}<br>"
        f"<strong>Total: Rs. {order.total}</strong></p>"
        f"{address}"
        f"<p>Payment: cash on delivery.</p>"
    )


def _summary_text(order: Order) -> str:
    lines = "\n".join(
        f"  {item.quantity} x {item.menu_item_name or 'Item'} - Rs. {item.line_total}"
        for item in order.items.all()
    )
    address = f"Deliver to: {order.delivery_address}\n" if order.delivery_address else ""
    return (
        f"Hi {order.user.get_short_name()},\n\n"
        f"Order {order.pk} at "
        f"{order.restaurant.name if order.restaurant_id else 'FoodFlow'}:\n"
        f"{lines}\n\n"
        f"Subtotal: Rs. {order.subtotal}\n"
        f"Delivery fee: Rs. {order.delivery_fee}\n"
        f"Total: Rs. {order.total}\n"
        f"{address}"
        f"Payment: cash on delivery."
    )


def _send(subject: str, text: str, html: str, recipient: str) -> None:
    message = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    message.attach_alternative(html, "text/html")
    message.send()


@shared_task(name="apps.orders.tasks.send_order_confirmation_email")
def send_order_confirmation_email(order_id: str) -> None:
    """Itemized confirmation to the customer right after checkout."""
    order = _get_order(order_id)
    if order is None or not order.user.email:
        return
    restaurant = order.restaurant.name if order.restaurant_id else "FoodFlow"
    _send(
        subject=f"Your order at {restaurant} is awaiting confirmation",
        text=_summary_text(order),
        html=_summary_html(order),
        recipient=order.user.email,
    )


@shared_task(name="apps.orders.tasks.send_new_order_email")
def send_new_order_email(order_id: str) -> None:
    """Alert the restaurant owner about a new pending order."""
    order = _get_order(order_id)
    if order is None or order.restaurant_id is None:
        return
    owner = order.restaurant.owner
    if owner is None or not owner.email:
        return
    restaurant = order.restaurant.name
    _send(
        subject=f"New order {order.pk} at {restaurant} (Rs. {order.total})",
        text=(
            f"A new pending order arrived at {restaurant}.\n"
            f"Order {order.pk}: {order.item_count} item(s), total Rs. {order.total}.\n"
            f"Customer: {order.user.email or order.user.get_short_name()}\n"
            f"Deliver to: {order.delivery_address or 'no address provided'}\n"
            "Update the order status in the admin panel when ready."
        ),
        html=(
            f"<p>A new pending order arrived at <strong>{restaurant}</strong>.</p>"
            f"<p>Order <strong>{order.pk}</strong>: {order.item_count} item(s), "
            f"total <strong>Rs. {order.total}</strong>.</p>"
            f"<p>Customer: {order.user.email or order.user.get_short_name()}<br>"
            f"Deliver to: {order.delivery_address or 'no address provided'}</p>"
        ),
        recipient=owner.email,
    )


@shared_task(name="apps.orders.tasks.send_order_status_email")
def send_order_status_email(order_id: str, new_status: str | None = None) -> None:
    """Tell the customer an order moved to a new lifecycle state.

    ``new_status`` is the state the transition was made to; it is preferred
    over re-reading the order so back-to-back changes mail the right state.
    """
    order = _get_order(order_id)
    if order is None or not order.user.email:
        return
    status = new_status or order.status
    label = STATUS_LABELS.get(status, status)
    restaurant = order.restaurant.name if order.restaurant_id else "FoodFlow"
    _send(
        subject=f"Order {order.pk} update: {label}",
        text=f"Your order {order.pk} at {restaurant} is now {label}. Total: Rs. {order.total}.",
        html=f"<p>Your order <strong>{order.pk}</strong> at {restaurant} "
        f"is now <strong>{label}</strong>. Total: Rs. {order.total}.</p>",
        recipient=order.user.email,
    )
