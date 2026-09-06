"""Ownership permissions shared by restaurants + menu viewsets.

Rule: safe methods are public (storefront browsing); writes require an
authenticated staff user or the restaurant's owner.
"""

from rest_framework import permissions


def restaurant_of(obj):
    """Resolve the Restaurant behind a Restaurant/Category/MenuItem/Modifier."""
    if hasattr(obj, "owner"):
        return obj
    restaurant = getattr(obj, "restaurant", None)
    if restaurant is not None:
        return restaurant
    category = getattr(obj, "category", None)
    if category is not None:
        return category.restaurant
    group = getattr(obj, "group", None)
    if group is not None:
        return group.restaurant
    return None


class IsRestaurantOwnerOrReadOnly(permissions.BasePermission):
    """Public read; writes need staff or the owning user."""

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
        if user.is_staff:
            return True
        restaurant = restaurant_of(obj)
        return restaurant is not None and restaurant.owner_id == user.id


def ensure_can_write_restaurant(user, restaurant):
    """Raise PermissionDenied unless staff or owner (for create actions)."""
    from rest_framework.exceptions import PermissionDenied

    if user.is_staff:
        return
    if restaurant is None or restaurant.owner_id != user.id:
        raise PermissionDenied("You do not own this restaurant.")
