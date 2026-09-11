"""Cart serializers: live totals, modifier-aware validation."""

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from apps.carts.models import MAX_QUANTITY, Cart, CartItem
from apps.menu.models import MenuItem, ModifierOption


class CartOptionDetailSerializer(serializers.ModelSerializer):
    group_name = serializers.ReadOnlyField(source="group.name")

    class Meta:
        model = ModifierOption
        fields = ["id", "name", "price_delta", "group", "group_name"]
        read_only_fields = fields


class CartItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.ReadOnlyField(source="menu_item.name")
    unit_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    line_total = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    selected_options_detail = CartOptionDetailSerializer(
        source="selected_options", many=True, read_only=True
    )

    class Meta:
        model = CartItem
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
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "menu_item_name",
            "unit_price",
            "line_total",
            "selected_options_detail",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {"quantity": {"min_value": 1, "max_value": MAX_QUANTITY}}

    def validate(self, attrs):
        instance = self.instance
        item = attrs.get("menu_item", getattr(instance, "menu_item", None))
        if item is None:
            raise serializers.ValidationError({"menu_item": "This field is required."})
        if (
            not item.is_available
            or not item.category.is_active
            or not item.category.restaurant.is_active
        ):
            raise serializers.ValidationError(
                {"menu_item": "This item is currently unavailable."}
            )

        options = attrs.get("selected_options", None)
        if options is None and instance is not None:
            options = list(instance.selected_options.all())
        options = list(options or [])
        for option in options:
            if not option.is_available or not option.group.is_active:
                raise serializers.ValidationError(
                    {"selected_options": f'"{option.name}" is currently unavailable.'}
                )
            if option.group.restaurant_id != item.category.restaurant_id:
                raise serializers.ValidationError(
                    {
                        "selected_options": (
                            f'"{option.name}" does not belong to this restaurant.'
                        )
                    }
                )
        allowed_group_ids = set(item.modifier_groups.values_list("id", flat=True))
        for option in options:
            if option.group_id not in allowed_group_ids:
                raise serializers.ValidationError(
                    {
                        "selected_options": (
                            f'"{option.name}" is not offered with "{item.name}".'
                        )
                    }
                )
        picks_per_group: dict[int, int] = {}
        for option in options:
            picks_per_group[option.group_id] = (
                picks_per_group.get(option.group_id, 0) + 1
            )
        for group in item.modifier_groups.all():
            picked = picks_per_group.get(group.id, 0)
            if picked < group.min_select or picked > group.max_select:
                raise serializers.ValidationError(
                    {
                        "selected_options": (
                            f'"{group.name}" needs between {group.min_select} and '
                            f"{group.max_select} selection(s); got {picked}."
                        )
                    }
                )
        return attrs


class CartSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.ReadOnlyField(source="restaurant.name")
    items = CartItemSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Cart
        fields = [
            "id",
            "restaurant",
            "restaurant_name",
            "items",
            "item_count",
            "subtotal",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


def get_user_cart(user) -> Cart:
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def get_user_line(user, pk: int) -> CartItem:
    return get_object_or_404(CartItem, pk=pk, cart__user=user)
