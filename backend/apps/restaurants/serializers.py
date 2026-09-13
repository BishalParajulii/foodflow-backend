"""Minimal restaurant serializers (full profile lands later)."""

from rest_framework import serializers

from apps.accounts.models import Role
from apps.restaurants.models import Branch, Restaurant


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = [
            "id",
            "restaurant",
            "name",
            "slug",
            "address",
            "phone",
            "latitude",
            "longitude",
            "opening_time",
            "closing_time",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "restaurant", "slug", "created_at", "updated_at"]


class RestaurantSerializer(serializers.ModelSerializer):
    owner_email = serializers.ReadOnlyField(source="owner.email")
    branches = BranchSerializer(many=True, read_only=True)
    branches_count = serializers.SerializerMethodField(read_only=True)
    rating_average = serializers.SerializerMethodField(read_only=True)
    review_count = serializers.SerializerMethodField(read_only=True)

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
            "branches",
            "branches_count",
            "rating_average",
            "review_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "owner_email",
            "slug",
            "branches",
            "branches_count",
            "rating_average",
            "review_count",
            "created_at",
            "updated_at",
        ]

    def get_branches_count(self, obj: Restaurant) -> int:
        return obj.branches.count()

    def get_rating_average(self, obj: Restaurant):
        from django.db.models import Avg

        avg = obj.reviews.filter(is_visible=True).aggregate(v=Avg("rating"))["v"]
        return round(avg, 2) if avg is not None else None

    def get_review_count(self, obj: Restaurant) -> int:
        return obj.reviews.filter(is_visible=True).count()


class RestaurantCreateMixin:
    """Sets owner=request.user and upgrades customers to restaurant_owner."""

    def perform_create(self, serializer):
        restaurant = serializer.save(owner=self.request.user)
        user = self.request.user
        if user.role == Role.CUSTOMER:
            user.role = Role.RESTAURANT_OWNER
            user.save(update_fields=["role", "updated_at"])
        return restaurant
