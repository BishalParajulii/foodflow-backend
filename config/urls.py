"""Root URL configuration (scaffolding only).

Exposes:
- /admin/            Django admin (no app models registered yet)
- /api/v1/           Versioned API placeholder namespace (no app endpoints yet)
- /api/schema/       OpenAPI schema placeholder (drf-spectacular)
- /api/docs/         Swagger UI placeholder
- /                  Minimal project-level placeholder response
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def api_v1_root(request):
    """Project-level `/api/v1/` placeholder (not a business endpoint)."""
    return Response(
        {
            "name": "FoodFlow API",
            "version": "v1",
            "status": "scaffolding only — no app endpoints yet",
            "docs": "/api/docs/",
            "schema": "/api/schema/",
        }
    )


def project_root(request):
    """Minimal project root placeholder."""
    return JsonResponse(
        {
            "project": "FoodFlow",
            "status": "scaffolding only",
            "api": "/api/v1/",
        }
    )


urlpatterns = [
    path("", project_root, name="project-root"),
    path("admin/", admin.site.urls),
    path("api/v1/", api_v1_root, name="api-v1-root"),
    path("api/v1/auth/", include("apps.accounts.urls")),
    # Future app endpoints (NOT implemented in this phase):
    # path("api/v1/restaurants/", include("apps.restaurants.urls")),
    # path("api/v1/menu/", include("apps.menu.urls")),
    # path("api/v1/cart/", include("apps.carts.urls")),
    # path("api/v1/orders/", include("apps.orders.urls")),
    # path("api/v1/payments/", include("apps.payments.urls")),
    # path("api/v1/delivery/", include("apps.delivery.urls")),
    # path("api/v1/locations/", include("apps.locations.urls")),
    # path("api/v1/notifications/", include("apps.notifications.urls")),
    # path("api/v1/reviews/", include("apps.reviews.urls")),
    # path("api/v1/promotions/", include("apps.promotions.urls")),
    # path("api/v1/analytics/", include("apps.analytics.urls")),
    # OpenAPI placeholders:
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
