"""Order serializers: frozen read model, checkout input, status changes."""

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from apps.orders.models import (
    CUSTOMER_CANCELLABLE_FROM,
    Order,
    OrderItem,
    OrderStatus,
)
from apps.restaurants.permissions import is_platform_admin


class OrderItemSerializer(serializers.ModelSerializer):
    selected_options_detail = serializers.JSONField(
        source="selected_options_snapshot", read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "menu_item",
            "menu_item_name",
            "quantity",
            "unit_price",
            "line_total",
            "selected_options",
            "selected_options_detail",
            "created_at",
        ]
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")
    restaurant_name = serializers.ReadOnlyField(source="restaurant.name")
    items = OrderItemSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "user_email",
            "restaurant",
            "restaurant_name",
            "status",
            "items",
            "item_count",
            "subtotal",
            "delivery_fee",
            "total",
            "delivery_address",
            "phone",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class OrderCreateSerializer(serializers.Serializer):
    """Checkout input: cart is the source of lines; only contact fields here."""

    delivery_address = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=""
    )
    phone = serializers.CharField(
        max_length=20, required=False, allow_blank=True, default=""
    )
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=OrderStatus.choices)

    def validate_status(self, value):
        order: Order | None = getattr(self, "instance", None)
        request = self.context.get("request")
        if order is None or request is None:
            return value
        if value == order.status:
            return value
        if not order.can_transition_to(value):
            raise serializers.ValidationError(
                f"Cannot move order from {order.status} to {value}."
            )
        user = request.user
        if is_platform_admin(user):
            return value
        is_restaurant_owner = order.restaurant.owner_id == user.id
        is_customer = order.user_id == user.id
        if value == OrderStatus.CANCELLED:
            if is_restaurant_owner:
                return value
            if is_customer and order.status in CUSTOMER_CANCELLABLE_FROM:
                return value
            if is_customer:
                raise serializers.ValidationError(
                    "You can only cancel a pending or confirmed order."
                )
            raise PermissionDenied("You cannot cancel this order.")
        if not is_restaurant_owner:
            raise PermissionDenied("Only the restaurant can update this order.")
        return value
