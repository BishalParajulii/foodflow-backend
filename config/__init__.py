"""Django project configuration package (no business logic)."""

from .celery import app as celery_app

__all__ = ("celery_app",)
