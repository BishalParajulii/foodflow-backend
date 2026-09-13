"""Notification serializers: users may only flip the read flag."""

from django.utils import timezone
from rest_framework import serializers

from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "type",
            "title",
            "body",
            "order",
            "is_read",
            "read_at",
            "created_at",
        ]
        read_only_fields = ["id", "type", "title", "body", "order", "read_at", "created_at"]

    def update(self, instance, validated_data):
        instance.is_read = validated_data.get("is_read", instance.is_read)
        instance.read_at = timezone.now() if instance.is_read else None
        instance.save(update_fields=["is_read", "read_at", "updated_at"])
        return instance
