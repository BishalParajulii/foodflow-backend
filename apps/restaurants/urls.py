"""Restaurant URL namespace: /api/v1/restaurants/."""

from rest_framework.routers import DefaultRouter

from apps.restaurants.views import RestaurantViewSet

app_name = "restaurants"

router = DefaultRouter()
router.register("", RestaurantViewSet, basename="restaurant")

urlpatterns = router.urls
