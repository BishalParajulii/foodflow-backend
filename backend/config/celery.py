"""Celery bootstrap: order lifecycle email tasks (see apps.orders.tasks)."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("foodflow")

# Load `CELERY_*` settings from Django settings.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover `tasks.py` modules in all installed apps (apps.orders.tasks).
app.autodiscover_tasks()
