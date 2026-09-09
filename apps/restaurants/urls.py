"""Restaurant URL namespace: /api/v1/restaurants/.

Branches are managed nested under their restaurant — one place:
/api/v1/restaurants/<restaurant_pk>/branches/
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.restaurants.views import BranchViewSet, RestaurantViewSet

app_name = "restaurants"

router = DefaultRouter()
router.register("", RestaurantViewSet, basename="restaurant")

branch_list = BranchViewSet.as_view({"get": "list", "post": "create"})
branch_detail = BranchViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)

urlpatterns = [
    path("<uuid:restaurant_pk>/branches/", branch_list, name="branch-list"),
    path("<uuid:restaurant_pk>/branches/<uuid:pk>/", branch_detail, name="branch-detail"),
    *router.urls,
]
