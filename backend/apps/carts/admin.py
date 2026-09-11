"""Admin for carts."""

from django.contrib import admin

from apps.carts.models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ("menu_item", "quantity")
    show_change_link = True


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "restaurant", "item_count", "updated_at")
    search_fields = ("user__email", "restaurant__name")
    readonly_fields = ("created_at", "updated_at")
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("menu_item", "cart", "quantity")
    search_fields = ("menu_item__name", "cart__user__email")
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("selected_options",)
