"""Cart endpoints: per-user singleton, auth required throughout.

- GET /api/v1/cart/ — current cart (empty 200 when new).
- POST /api/v1/cart/items/ — add a line (merges same item + modifiers).
- PATCH/DELETE /api/v1/cart/items/<id>/ — change quantity / remove a line.
- DELETE /api/v1/cart/clear/ — empty the cart.
"""

from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.views import APIView

from apps.common.responses import error_response, success_response

from apps.carts.serializers import (
    CartItemSerializer,
    CartSerializer,
    get_user_cart,
    get_user_line,
)
from apps.carts.models import MAX_QUANTITY


class CartDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Cart"], responses=CartSerializer, summary="Get my cart")
    def get(self, request):
        return success_response(
            CartSerializer(get_user_cart(request.user)).data,
            message="Cart retrieved successfully.",
        )


class CartItemCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Cart"],
        request=CartItemSerializer,
        responses={200: CartSerializer},
        summary="Add an item to my cart",
    )
    def post(self, request):
        cart = get_user_cart(request.user)
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.validated_data["menu_item"]
        options = list(serializer.validated_data.get("selected_options", []))

        if cart.restaurant_id is None:
            cart.restaurant = item.category.restaurant
            cart.save(update_fields=["restaurant", "updated_at"])
        elif cart.restaurant_id != item.category.restaurant_id:
            return error_response(
                "Your cart has items from another restaurant. "
                "Clear it first (DELETE /api/v1/cart/clear/).",
                code="different_restaurant",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        line = cart.find_line(item, {o.id for o in options})
        if line is None:
            line = serializer.save(cart=cart)
        else:
            line.quantity = min(
                line.quantity + serializer.validated_data["quantity"], MAX_QUANTITY
            )
            line.save(update_fields=["quantity", "updated_at"])
        cart.refresh_from_db()
        return success_response(
            CartSerializer(cart).data, message="Item added to cart."
        )


class CartItemDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Cart"],
        request=CartItemSerializer,
        responses=CartItemSerializer,
        summary="Change a cart line's quantity/options",
    )
    def patch(self, request, pk):
        line = get_user_line(request.user, pk)
        serializer = CartItemSerializer(line, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(serializer.data, message="Cart line updated.")

    @extend_schema(tags=["Cart"], summary="Remove a line from my cart")
    def delete(self, request, pk):
        line = get_user_line(request.user, pk)
        cart = line.cart
        line.delete()
        cart.reset_restaurant_if_empty()
        return success_response(
            CartSerializer(cart).data, message="Cart line removed."
        )


class CartClearView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Cart"], responses=CartSerializer, summary="Empty my cart")
    def delete(self, request):
        cart = get_user_cart(request.user)
        cart.items.all().delete()
        cart.reset_restaurant_if_empty()
        return success_response(
            CartSerializer(cart).data, message="Cart cleared successfully."
        )
