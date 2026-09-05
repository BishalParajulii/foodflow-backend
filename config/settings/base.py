"""Shared Django settings (all environments).

Scaffolding only: no business logic lives here.
Environment-specific overrides live in local.py / production.py / test.py.
"""

from pathlib import Path
from datetime import timedelta

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    DATABASE_URL=(str, f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
    REDIS_URL=(str, ""),
    CELERY_BROKER_URL=(str, "redis://localhost:6379/0"),
    CELERY_RESULT_BACKEND=(str, "redis://localhost:6379/0"),
    EMAIL_HOST=(str, "localhost"),
    EMAIL_PORT=(int, 25),
    EMAIL_HOST_USER=(str, ""),
    EMAIL_HOST_PASSWORD=(str, ""),
    EMAIL_USE_TLS=(bool, False),
    DEFAULT_FROM_EMAIL=(str, "noreply@foodflow.local"),
)

# Load `.env` when present (never required, never committed).
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    environ.Env.read_env(_env_file, overwrite=False)

SECRET_KEY = env("SECRET_KEY", default="django-insecure-foodflow-scaffolding-only")

DEBUG = env("DEBUG")

ALLOWED_HOSTS: list[str] = env("ALLOWED_HOSTS")

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "channels",
    "rest_framework_simplejwt.token_blacklist",
]

LOCAL_APPS = [
    "apps.accounts.apps.AccountsConfig",
    "apps.restaurants.apps.RestaurantsConfig",
    "apps.menu.apps.MenuConfig",
    "apps.carts.apps.CartsConfig",
    "apps.orders.apps.OrdersConfig",
    "apps.payments.apps.PaymentsConfig",
    "apps.delivery.apps.DeliveryConfig",
    "apps.locations.apps.LocationsConfig",
    "apps.notifications.apps.NotificationsConfig",
    "apps.reviews.apps.ReviewsConfig",
    "apps.promotions.apps.PromotionsConfig",
    "apps.analytics.apps.AnalyticsConfig",
    "apps.common.apps.CommonConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database — PostgreSQL-ready via DATABASE_URL, SQLite fallback for boot.
# ---------------------------------------------------------------------------
DATABASES = {
    "default": env.db("DATABASE_URL"),
}

# ---------------------------------------------------------------------------
# Authentication / custom user.
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static / media
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Django REST Framework — foundation only (no endpoints yet).
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    # Throttling placeholder (rates tuned later per endpoint).
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
    # OpenAPI schema generation (drf-spectacular).
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "FoodFlow API",
    "DESCRIPTION": "Food delivery platform API (scaffolding — no endpoints yet).",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ---------------------------------------------------------------------------
# SimpleJWT — email-login auth (tokens issued by apps.accounts).
# ---------------------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=env.int("JWT_ACCESS_MINUTES", default=60)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_DAYS", default=7)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# ---------------------------------------------------------------------------
# Google (Gmail) login — verify ID tokens issued by Google Identity Services.
# Frontend obtains an ID token and POSTs it to /api/v1/auth/google/.
# ---------------------------------------------------------------------------
GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID", default="")

# ---------------------------------------------------------------------------
# Cache — Redis-ready, locmem by default (no Redis server required to boot).
# ---------------------------------------------------------------------------
REDIS_URL = env("REDIS_URL")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

# ---------------------------------------------------------------------------
# Channels — Channels-ready, in-memory by default.
# Production switches to RedisChannelLayer (see production.py).
# ---------------------------------------------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# ---------------------------------------------------------------------------
# Celery — Celery-ready (no tasks defined yet, no worker required to boot).
# ---------------------------------------------------------------------------
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# ---------------------------------------------------------------------------
# Email (placeholder configuration)
# ---------------------------------------------------------------------------
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
