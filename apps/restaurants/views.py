"""Minimal restaurant endpoints (public read, owner write)."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, viewsets

from apps.restaurants.models import Restaurant
from apps.restaurants.permissions import IsRestaurantOwnerOrReadOnly
from apps.restaurants.serializers import RestaurantCreateMixin, RestaurantSerializer


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
    queryset = Restaurant.objects.select_related("owner").all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsRestaurantOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "address"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]
