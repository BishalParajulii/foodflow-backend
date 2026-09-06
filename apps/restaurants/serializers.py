"""Minimal restaurant serializers (full profile lands later)."""

from rest_framework import serializers

from apps.accounts.models import Role
from apps.restaurants.models import Restaurant


class RestaurantSerializer(serializers.ModelSerializer):
    owner_email = serializers.ReadOnlyField(source="owner.email")

    class Meta:
        model = Restaurant
        fields = [
            "id",
            "owner",
            "owner_email",
            "name",
            "slug",
            "description",
            "phone",
            "address",
            "logo_url",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "owner_email", "slug", "created_at", "updated_at"]


class RestaurantCreateMixin:
    """Sets owner=request.user and upgrades customers to restaurant_owner."""

    def perform_create(self, serializer):
        restaurant = serializer.save(owner=self.request.user)
        user = self.request.user
        if user.role == Role.CUSTOMER:
            user.role = Role.RESTAURANT_OWNER
            user.save(update_fields=["role", "updated_at"])
        return restaurant
