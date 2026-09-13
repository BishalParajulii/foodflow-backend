"""Notification admin: browse per user, filter unread."""

from django.contrib import admin

from apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "type", "title", "order", "is_read", "created_at"]
    list_filter = ["type", "is_read", "created_at"]
    search_fields = ["user__email", "title", "body"]
    readonly_fields = ["created_at", "updated_at"]
