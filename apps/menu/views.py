"""Menu endpoints: public read, restaurant-owner write."""

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, viewsets

from apps.menu.filters import CategoryFilter, MenuItemFilter, ModifierGroupFilter
from apps.menu.models import Category, MenuItem, ModifierGroup, ModifierOption
from apps.menu.serializers import (
    CategorySerializer,
    MenuItemSerializer,
    ModifierGroupSerializer,
    ModifierOptionSerializer,
)
from apps.restaurants.permissions import (
    IsRestaurantOwnerOrReadOnly,
    ensure_can_write_restaurant,
)


@extend_schema(tags=["Menu"])
@extend_schema_view(
    list=extend_schema(summary="List menu categories"),
    retrieve=extend_schema(summary="Get a menu category"),
    create=extend_schema(summary="Create a category (restaurant owner)"),
    partial_update=extend_schema(summary="Update a category"),
    update=extend_schema(summary="Replace a category"),
    destroy=extend_schema(summary="Delete a category"),
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.select_related("restaurant").all()
    serializer_class = CategorySerializer
    permission_classes = [IsRestaurantOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CategoryFilter
    search_fields = ["name", "description"]
    ordering_fields = ["sort_order", "name", "created_at"]
    ordering = ["sort_order", "name"]

    def perform_create(self, serializer):
        ensure_can_write_restaurant(self.request.user, serializer.validated_data["restaurant"])
        serializer.save()


@extend_schema(tags=["Menu"])
@extend_schema_view(
    list=extend_schema(summary="List menu items"),
    retrieve=extend_schema(summary="Get a menu item with its modifiers"),
    create=extend_schema(summary="Create a menu item (restaurant owner)"),
    partial_update=extend_schema(summary="Update a menu item"),
    update=extend_schema(summary="Replace a menu item"),
    destroy=extend_schema(summary="Delete a menu item"),
)
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = (
        MenuItem.objects.select_related("category", "category__restaurant")
        .prefetch_related("modifier_groups__options")
        .all()
    )
    serializer_class = MenuItemSerializer
    permission_classes = [IsRestaurantOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MenuItemFilter
    search_fields = ["name", "description"]
    ordering_fields = ["sort_order", "name", "price", "created_at"]
    ordering = ["sort_order", "name"]

    def perform_create(self, serializer):
        category = serializer.validated_data["category"]
        ensure_can_write_restaurant(self.request.user, category.restaurant)
        serializer.save()


@extend_schema(tags=["Menu"])
@extend_schema_view(
    list=extend_schema(summary="List modifier groups"),
    retrieve=extend_schema(summary="Get a modifier group with options"),
    create=extend_schema(summary="Create a modifier group (restaurant owner)"),
    partial_update=extend_schema(summary="Update a modifier group"),
    update=extend_schema(summary="Replace a modifier group"),
    destroy=extend_schema(summary="Delete a modifier group"),
)
class ModifierGroupViewSet(viewsets.ModelViewSet):
    queryset = ModifierGroup.objects.select_related("restaurant").prefetch_related(
        "options"
    )
    serializer_class = ModifierGroupSerializer
    permission_classes = [IsRestaurantOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ModifierGroupFilter
    search_fields = ["name", "description"]
    ordering_fields = ["sort_order", "name", "created_at"]
    ordering = ["sort_order", "name"]

    def perform_create(self, serializer):
        ensure_can_write_restaurant(self.request.user, serializer.validated_data["restaurant"])
        serializer.save()


@extend_schema(tags=["Menu"])
@extend_schema_view(
    list=extend_schema(summary="List modifier options"),
    retrieve=extend_schema(summary="Get a modifier option"),
    create=extend_schema(summary="Create a modifier option (restaurant owner)"),
    partial_update=extend_schema(summary="Update a modifier option"),
    update=extend_schema(summary="Replace a modifier option"),
    destroy=extend_schema(summary="Delete a modifier option"),
)
class ModifierOptionViewSet(viewsets.ModelViewSet):
    queryset = ModifierOption.objects.select_related("group", "group__restaurant").all()
    serializer_class = ModifierOptionSerializer
    permission_classes = [IsRestaurantOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {"group": ["exact"], "is_available": ["exact"]}
    search_fields = ["name"]
    ordering_fields = ["sort_order", "name", "price_delta", "created_at"]
    ordering = ["sort_order", "name"]

    def perform_create(self, serializer):
        group = serializer.validated_data["group"]
        ensure_can_write_restaurant(self.request.user, group.restaurant)
        serializer.save()
