from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.orders"
    verbose_name = "Orders"

    def ready(self):
        # Register order -> email dispatch signals (Celery tasks).
        from apps.orders import signals  # noqa: F401
