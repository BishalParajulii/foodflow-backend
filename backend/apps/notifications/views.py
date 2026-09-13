"""Notification inbox: scoped to the logged-in user."""

from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.mixins import SuccessResponseMixin
from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer


@extend_schema(tags=["Notifications"])
@extend_schema_view(
    list=extend_schema(summary="List my notifications"),
    retrieve=extend_schema(summary="Get a notification"),
    partial_update=extend_schema(summary="Mark a notification read/unread"),
    destroy=extend_schema(summary="Dismiss a notification"),
)
class NotificationViewSet(
    SuccessResponseMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    ordering = ["-created_at"]
    http_method_names = ["get", "patch", "delete", "post", "head", "options"]
    success_messages = {
        "partial_update": "Notification updated.",
        "mark_all_read": "All notifications marked as read.",
    }

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).select_related("order")

    @extend_schema(summary="Count my unread notifications")
    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        return Response({"unread_count": self.get_queryset().filter(is_read=False).count()})

    @extend_schema(summary="Mark all my notifications as read")
    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        now = timezone.now()
        updated = (
            self.get_queryset().filter(is_read=False).update(is_read=True, read_at=now)
        )
        return Response({"updated": updated})
