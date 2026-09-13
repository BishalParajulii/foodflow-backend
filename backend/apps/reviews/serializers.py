"""Review serializers: verified-purchase + duplicate rules."""

from rest_framework import serializers

from apps.orders.models import OrderStatus
from apps.reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")
    restaurant_name = serializers.ReadOnlyField(source="restaurant.name")

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "user_email",
            "restaurant",
            "restaurant_name",
            "order",
            "rating",
            "title",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "user_email",
            "restaurant_name",
            "created_at",
            "updated_at",
        ]

    def validate_order(self, order):
        request = self.context.get("request")
        if order is None or request is None:
            return order
        if order.user_id != request.user.id:
            raise serializers.ValidationError("You can only review your own orders.")
        if order.status != OrderStatus.DELIVERED:
            raise serializers.ValidationError("You can only review delivered orders.")
        restaurant = self.initial_data.get("restaurant") or getattr(
            self.instance, "restaurant_id", None
        )
        if restaurant and str(order.restaurant_id) != str(restaurant):
            raise serializers.ValidationError("Order does not belong to this restaurant.")
        if (
            Review.objects.filter(order=order)
            .exclude(pk=getattr(self.instance, "pk", None))
            .exists()
        ):
            raise serializers.ValidationError("This order already has a review.")
        return order

    def validate(self, attrs):
        request = self.context.get("request")
        restaurant = attrs.get("restaurant") or getattr(self.instance, "restaurant", None)
        order = attrs.get("order", getattr(self.instance, "order", None))
        # One open (order-less) review per user + restaurant.
        if restaurant and order is None and request is not None:
            qs = Review.objects.filter(
                user=request.user, restaurant=restaurant, order__isnull=True
            )
            if self.instance is not None:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "You have already reviewed this restaurant."
                )
        return attrs
