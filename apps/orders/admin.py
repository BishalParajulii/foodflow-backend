"""Admin for orders."""

from django.contrib import admin

from apps.orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("menu_item_name", "quantity", "unit_price", "line_total")
    readonly_fields = ("menu_item_name", "quantity", "unit_price", "line_total")
    show_change_link = True


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "restaurant", "status", "total", "created_at")
    list_filter = ("status", "restaurant")
    search_fields = ("user__email", "restaurant__name", "notes")
    readonly_fields = ("subtotal", "delivery_fee", "total", "created_at", "updated_at")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("menu_item_name", "order", "quantity", "line_total")
    search_fields = ("menu_item_name", "order__user__email")
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("selected_options",)
