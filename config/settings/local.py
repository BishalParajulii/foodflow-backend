"""Development settings."""

from .base import *  # noqa: F403, F401
from .base import env

DEBUG = True

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "testserver"])

# Console email backend for local development.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Keep the default SQLite DB from base.py unless DATABASE_URL is set.
# Keep locmem cache / in-memory channel layer unless REDIS_URL is set.

# DRF browsable API remains enabled locally (see base.py renderers).

# Development convenience: allow all CORS origins is NOT enabled here on
# purpose — add django-cors-headers later if a frontend appears.
