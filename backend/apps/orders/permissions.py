"""Order permissions: customer owns, restaurant owner manages, admins see all."""

from rest_framework import permissions

from apps.restaurants.permissions import is_platform_admin


class IsOrderParty(permissions.BasePermission):
    """Object access: order owner, restaurant owner, or platform admin."""

    message = "You do not have access to this order."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if is_platform_admin(user):
            return True
        if obj.user_id == user.id:
            return True
        return obj.restaurant.owner_id == user.id
