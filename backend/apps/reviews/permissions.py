"""Review permissions: public read, author-or-admin write."""

from rest_framework import permissions

from apps.restaurants.permissions import is_platform_admin


class IsReviewAuthorOrReadOnly(permissions.BasePermission):
    """Anyone may read; writes need auth and (author or admin) ownership."""

    message = "You can only modify your own reviews."

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if is_platform_admin(user):
            return True
        return obj.user_id == user.id
