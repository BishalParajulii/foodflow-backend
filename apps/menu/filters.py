"""Filters for menu browsing (all read endpoints are public)."""

import django_filters

from apps.menu.models import Category, MenuItem, ModifierGroup


class CategoryFilter(django_filters.FilterSet):
    class Meta:
        model = Category
        fields = {"restaurant": ["exact"], "is_active": ["exact"]}


class MenuItemFilter(django_filters.FilterSet):
    restaurant = django_filters.NumberFilter(
        field_name="category__restaurant", help_text="Filter by restaurant id."
    )
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = MenuItem
        fields = {
            "category": ["exact"],
            "is_veg": ["exact"],
            "is_available": ["exact"],
        }


class ModifierGroupFilter(django_filters.FilterSet):
    class Meta:
        model = ModifierGroup
        fields = {"restaurant": ["exact"], "is_active": ["exact"]}
