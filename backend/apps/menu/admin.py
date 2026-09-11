"""Admin for menu models."""

from django.contrib import admin

from apps.menu.models import Category, MenuItem, ModifierGroup, ModifierOption


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 0
    fields = ("name", "price", "is_veg", "is_available", "sort_order")
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "sort_order", "is_active")
    list_filter = ("restaurant", "is_active")
    search_fields = ("name", "restaurant__name")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    inlines = [MenuItemInline]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_veg", "is_available", "sort_order")
    list_filter = ("is_veg", "is_available", "category__restaurant")
    search_fields = ("name", "description", "category__name")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("modifier_groups",)


class ModifierOptionInline(admin.TabularInline):
    model = ModifierOption
    extra = 1
    fields = ("name", "price_delta", "is_available", "sort_order")


@admin.register(ModifierGroup)
class ModifierGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "min_select", "max_select", "is_active")
    list_filter = ("restaurant", "is_active")
    search_fields = ("name", "restaurant__name")
    readonly_fields = ("created_at", "updated_at")
    inlines = [ModifierOptionInline]


@admin.register(ModifierOption)
class ModifierOptionAdmin(admin.ModelAdmin):
    list_display = ("name", "group", "price_delta", "is_available")
    list_filter = ("is_available", "group__restaurant")
    search_fields = ("name", "group__name")
    readonly_fields = ("created_at", "updated_at")
