"""Order endpoints: checkout from cart, history, status lifecycle.

- POST /api/v1/orders/ — checkout my cart (frozen prices, clears cart).
- GET /api/v1/orders/ — my orders (owners also see their restaurant's).
- GET /api/v1/orders/<id>/ — detail (owner, restaurant owner, admin).
- PATCH /api/v1/orders/<id>/ — update ``status`` only.
- POST /api/v1/orders/<id>/cancel/ — cancel shortcut.
"""

from decimal import Decimal

from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.carts.serializers import get_user_cart
from apps.common.mixins import SuccessResponseMixin
from apps.common.responses import error_response
from apps.orders.filters import OrderFilter
from apps.orders.models import Order, OrderStatus
from apps.orders.permissions import IsOrderParty
from apps.orders.serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
)


def _snapshot_option(option):
    return {
        "id": str(option.id),
        "name": option.name,
        "price_delta": str(option.price_delta),
        "group": str(option.group_id),
        "group_name": option.group.name,
    }


def _validate_cart_for_checkout(cart):
    """Raise ValidationError if any cart line is no longer orderable."""
    lines = list(
        cart.items.select_related(
            "menu_item", "menu_item__category", "menu_item__category__restaurant"
        ).prefetch_related("selected_options__group", "menu_item__modifier_groups")
    )
    if not lines:
        return lines
    for line in lines:
        item = line.menu_item
        if (
            item is None
            or not item.is_available
            or not item.category.is_active
            or not item.category.restaurant.is_active
        ):
            raise ValidationError(
                {"cart": f'"{getattr(item, "name", "Item")}" is no longer available.'}
            )
        options = list(line.selected_options.all())
        for option in options:
            if not option.is_available or not option.group.is_active:
                raise ValidationError(
                    {"cart": f'"{option.name}" is no longer available.'}
                )
            if option.group.restaurant_id != cart.restaurant_id:
                raise ValidationError(
                    {"cart": f'"{option.name}" does not belong to this restaurant.'}
                )
        allowed = set(item.modifier_groups.values_list("id", flat=True))
        for option in options:
            if option.group_id not in allowed:
                raise ValidationError(
                    {"cart": f'"{option.name}" is not offered with "{item.name}".'}
                )
        picks: dict = {}
        for option in options:
            picks[option.group_id] = picks.get(option.group_id, 0) + 1
        for group in item.modifier_groups.all():
            picked = picks.get(group.id, 0)
            if picked < group.min_select or picked > group.max_select:
                raise ValidationError(
                    {
                        "cart": (
                            f'"{group.name}" needs between {group.min_select} and '
                            f"{group.max_select} selection(s) for "
                            f'"{item.name}"; got {picked}.'
                        )
                    }
                )
    return lines


@extend_schema(tags=["Orders"])
@extend_schema_view(
    list=extend_schema(summary="List my orders"),
    retrieve=extend_schema(summary="Get an order"),
    create=extend_schema(summary="Checkout my cart into an order"),
    partial_update=extend_schema(summary="Update an order's status"),
)
class OrderViewSet(SuccessResponseMixin, viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOrderParty]
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # DjangoFilterBackend is global default; declare explicitly for schema.
    search_fields = ["notes", "delivery_address", "restaurant__name"]
    ordering_fields = ["created_at", "total", "status"]
    ordering = ["-created_at"]
    http_method_names = ["get", "post", "patch", "head", "options"]
    success_messages = {
        "create": "Order placed successfully.",
        "partial_update": "Order status updated.",
        "cancel": "Order cancelled.",
    }

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Order.objects.none()
        return (
            Order.objects.for_user(user)
            .select_related("user", "restaurant")
            .prefetch_related("items__selected_options")
            .order_by("-created_at")
        )

    def get_permissions(self):
        # Create (checkout) only needs auth; object-level checks apply elsewhere.
        if self.action == "create":
            return [IsAuthenticated()]
        return super().get_permissions()

    @extend_schema(
        tags=["Orders"], request=OrderCreateSerializer, responses={201: OrderSerializer}
    )
    def create(self, request, *args, **kwargs):
        input_serializer = OrderCreateSerializer(data=request.data or {})
        input_serializer.is_valid(raise_exception=True)
        cart = get_user_cart(request.user)
        lines = _validate_cart_for_checkout(cart)
        if not lines:
            return error_response(
                "Your cart is empty.",
                code="empty_cart",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        restaurant = cart.restaurant
        if restaurant is None:  # defensive; lines imply a lock
            return error_response(
                "Your cart has no restaurant.",
                code="empty_cart",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        subtotal = Decimal("0.00")
        snapshots = []
        for line in lines:
            options = list(line.selected_options.all())
            extras = sum((o.price_delta for o in options), Decimal("0.00"))
            unit_price = (line.menu_item.price + extras).quantize(Decimal("0.00"))
            line_total = (unit_price * line.quantity).quantize(Decimal("0.00"))
            subtotal += line_total
            snapshots.append((line, options, unit_price, line_total))
        subtotal = subtotal.quantize(Decimal("0.00"))
        delivery_fee = Decimal("0.00")
        total = (subtotal + delivery_fee).quantize(Decimal("0.00"))

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                restaurant=restaurant,
                status=OrderStatus.PENDING,
                subtotal=subtotal,
                delivery_fee=delivery_fee,
                total=total,
                delivery_address=input_serializer.validated_data.get(
                    "delivery_address", ""
                ),
                phone=input_serializer.validated_data.get("phone", ""),
                notes=input_serializer.validated_data.get("notes", ""),
            )
            for line, options, unit_price, line_total in snapshots:
                item = order.items.create(
                    menu_item=line.menu_item,
                    menu_item_name=line.menu_item.name,
                    quantity=line.quantity,
                    unit_price=unit_price,
                    line_total=line_total,
                    selected_options_snapshot=[_snapshot_option(o) for o in options],
                )
                if options:
                    item.selected_options.set(options)
            cart.items.all().delete()
            cart.reset_restaurant_if_empty()

        data = OrderSerializer(order).data
        return Response(data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()
        if "status" not in request.data:
            raise ValidationError({"status": "This field is required."})
        extra = set(request.data.keys()) - {"status"}
        if extra:
            raise ValidationError(
                {"non_field_errors": f"Only 'status' can be updated; got {sorted(extra)}."}
            )
        serializer = OrderStatusUpdateSerializer(
            order, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        order.status = serializer.validated_data["status"]
        order.save(update_fields=["status", "updated_at"])
        return Response(OrderSerializer(order).data)

    @extend_schema(
        tags=["Orders"], request=None, responses=OrderSerializer, summary="Cancel an order"
    )
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(
            order, data={"status": OrderStatus.CANCELLED}, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        order.status = OrderStatus.CANCELLED
        order.save(update_fields=["status", "updated_at"])
        return Response(OrderSerializer(order).data)
