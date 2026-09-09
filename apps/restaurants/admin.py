"""Admin for restaurants + branches."""

from django.contrib import admin

from apps.restaurants.models import Branch, Restaurant


class BranchInline(admin.TabularInline):
    model = Branch
    extra = 0
    fields = ("name", "address", "phone", "is_active")
    show_change_link = True


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description", "owner__email")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    inlines = [BranchInline]


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "is_active")
    list_filter = ("restaurant", "is_active")
    search_fields = ("name", "address", "restaurant__name")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
