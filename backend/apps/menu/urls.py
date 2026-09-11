"""Menu URL namespace: /api/v1/menu/."""

from rest_framework.routers import DefaultRouter

from apps.menu.views import (
    CategoryViewSet,
    MenuItemViewSet,
    ModifierGroupViewSet,
    ModifierOptionViewSet,
)

app_name = "menu"

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("items", MenuItemViewSet, basename="menuitem")
router.register("modifier-groups", ModifierGroupViewSet, basename="modifiergroup")
router.register("modifier-options", ModifierOptionViewSet, basename="modifieroption")

urlpatterns = router.urls
