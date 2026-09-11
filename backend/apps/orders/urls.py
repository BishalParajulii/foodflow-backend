"""Order URL namespace: /api/v1/orders/ (authenticated users only)."""

from rest_framework.routers import DefaultRouter

from apps.orders.views import OrderViewSet

app_name = "orders"

router = DefaultRouter()
router.register("", OrderViewSet, basename="order")

urlpatterns = router.urls
