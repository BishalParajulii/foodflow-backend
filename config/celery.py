"""Celery bootstrap (ready only — no tasks are defined in this phase)."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("foodflow")

# Load `CELERY_*` settings from Django settings.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover `tasks.py` in installed apps once tasks are added later.
# No tasks exist yet.
app.autodiscover_tasks()
