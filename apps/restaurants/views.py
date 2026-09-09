"""Restaurant + branch endpoints.

Restaurants are public to browse; branch management lives nested under the
restaurant and is restricted to its owner or admins.
"""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, viewsets

from apps.restaurants.models import Branch, Restaurant
from apps.restaurants.permissions import IsBranchManager, IsRestaurantOwnerOrReadOnly
from apps.restaurants.serializers import (
    BranchSerializer,
    RestaurantCreateMixin,
    RestaurantSerializer,
)


@extend_schema(tags=["Restaurants"])
@extend_schema_view(
    list=extend_schema(summary="List restaurants"),
    retrieve=extend_schema(summary="Get a restaurant"),
    create=extend_schema(summary="Register a restaurant (become its owner)"),
    partial_update=extend_schema(summary="Update a restaurant"),
    update=extend_schema(summary="Replace a restaurant"),
    destroy=extend_schema(summary="Delete a restaurant"),
)
class RestaurantViewSet(RestaurantCreateMixin, viewsets.ModelViewSet):
    queryset = Restaurant.objects.select_related("owner").prefetch_related("branches")
    serializer_class = RestaurantSerializer
    permission_classes = [IsRestaurantOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "address"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]


@extend_schema(tags=["Restaurants"])
@extend_schema_view(
    list=extend_schema(summary="List branches of a restaurant (owner/admin)"),
    retrieve=extend_schema(summary="Get a branch (owner/admin)"),
    create=extend_schema(summary="Add a branch (owner/admin)"),
    partial_update=extend_schema(summary="Update a branch (owner/admin)"),
    update=extend_schema(summary="Replace a branch (owner/admin)"),
    destroy=extend_schema(summary="Delete a branch (owner/admin)"),
)
class BranchViewSet(viewsets.ModelViewSet):
    serializer_class = BranchSerializer
    permission_classes = [IsBranchManager]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "address"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_parent_restaurant(self) -> Restaurant:
        return get_object_or_404(Restaurant, pk=self.kwargs["restaurant_pk"])

    def get_queryset(self):
        return Branch.objects.filter(
            restaurant_id=self.kwargs.get("restaurant_pk")
        ).select_related("restaurant")

    def perform_create(self, serializer):
        serializer.save(restaurant=self.get_parent_restaurant())
