"""Production settings (placeholders — not yet deployed).

All secrets come from environment variables. Nothing is hard-coded.
"""

from .base import *  # noqa: F403, F401
from .base import REDIS_URL, REST_FRAMEWORK, env

DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
# Deployment must provide ALLOWED_HOSTS, e.g.:
#   ALLOWED_HOSTS=api.foodflow.example.com

# ---------------------------------------------------------------------------
# Security / HTTPS
# ---------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------------------------
# Database — production expects DATABASE_URL to point at PostgreSQL, e.g.:
#   DATABASE_URL=postgres://USER:PASSWORD@HOST:5432/DB_NAME
# ---------------------------------------------------------------------------
# Inherited from base.py via env.db("DATABASE_URL"). No override needed.

# ---------------------------------------------------------------------------
# Cache / Channels — use Redis in production when REDIS_URL is set.
# ---------------------------------------------------------------------------
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [REDIS_URL]},
        }
    }

# ---------------------------------------------------------------------------
# DRF — JSON only in production (no browsable API).
# ---------------------------------------------------------------------------
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # type: ignore[index]
    "rest_framework.renderers.JSONRenderer",
]

# ---------------------------------------------------------------------------
# Email — configure a real backend via environment in production.
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# ---------------------------------------------------------------------------
# Logging — production placeholder (JSON/console handlers, INFO level).
# Tune formatters/handlers/shipper when deploying.
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": env.str("DJANGO_LOG_LEVEL", default="INFO"),
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": env.str("DJANGO_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
    },
}
