"""Review admin: moderate visibility, browse by restaurant/rating."""

from django.contrib import admin

from apps.reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "restaurant", "user", "rating", "order", "is_visible", "created_at"]
    list_filter = ["rating", "is_visible", "created_at"]
    search_fields = ["restaurant__name", "user__email", "title", "comment"]
    readonly_fields = ["created_at", "updated_at"]
