"""Menu serializers: categories, items (nested modifiers), modifier groups."""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.menu.models import Category, MenuItem, ModifierGroup, ModifierOption


class CategorySerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "restaurant",
            "name",
            "slug",
            "description",
            "image_url",
            "sort_order",
            "is_active",
            "items_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "items_count", "created_at", "updated_at"]

    def get_items_count(self, obj: Category) -> int:
        return obj.items.count()


class ModifierOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModifierOption
        fields = [
            "id",
            "group",
            "name",
            "price_delta",
            "sort_order",
            "is_available",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ModifierGroupSerializer(serializers.ModelSerializer):
    options = ModifierOptionSerializer(many=True, read_only=True)

    class Meta:
        model = ModifierGroup
        fields = [
            "id",
            "restaurant",
            "name",
            "description",
            "min_select",
            "max_select",
            "sort_order",
            "is_active",
            "options",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "options", "created_at", "updated_at"]

    def validate(self, attrs):
        instance = self.instance
        try:
            ModifierGroup(
                min_select=attrs.get("min_select", getattr(instance, "min_select", 0)),
                max_select=attrs.get("max_select", getattr(instance, "max_select", 1)),
            ).clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)
        return attrs


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.name")
    restaurant_id = serializers.ReadOnlyField(source="category.restaurant.id")
    modifier_groups_detail = ModifierGroupSerializer(
        source="modifier_groups", many=True, read_only=True
    )

    class Meta:
        model = MenuItem
        fields = [
            "id",
            "category",
            "category_name",
            "restaurant_id",
            "name",
            "slug",
            "description",
            "price",
            "compare_at_price",
            "image_url",
            "is_veg",
            "is_available",
            "preparation_time_minutes",
            "sort_order",
            "modifier_groups",
            "modifier_groups_detail",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "category_name",
            "restaurant_id",
            "modifier_groups_detail",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        instance = self.instance
        try:
            MenuItem(
                price=attrs.get("price", getattr(instance, "price", None)),
                compare_at_price=attrs.get(
                    "compare_at_price", getattr(instance, "compare_at_price", None)
                ),
            ).clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)
        return attrs
