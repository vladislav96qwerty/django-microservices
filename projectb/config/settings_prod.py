"""Production settings for ProjectB (Warehouse) — used on Render."""
import os

import dj_database_url

from .settings import *  # noqa: F401,F403
from .settings import BASE_DIR, REST_FRAMEWORK, env, env_bool  # noqa: F401


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
DEBUG = env_bool("DJANGO_DEBUG", False)

SECRET_KEY = env("PROJECTB_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("PROJECTB_SECRET_KEY must be set in production.")

RENDER_HOSTNAME = env("RENDER_EXTERNAL_HOSTNAME", "")
EXTRA_HOSTS = [h.strip() for h in env("PROJECTB_ALLOWED_HOSTS", "").split(",") if h.strip()]
ALLOWED_HOSTS = list({RENDER_HOSTNAME, *EXTRA_HOSTS, ".onrender.com"} - {""})

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASE_URL = env("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be provided in production.")

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    )
}

# ---------------------------------------------------------------------------
# Cache & Celery
# ---------------------------------------------------------------------------
REDIS_URL = env("REDIS_URL")
if not REDIS_URL:
    raise RuntimeError("REDIS_URL must be provided in production.")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_URL}/0",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "KEY_PREFIX": "projectb",
        "TIMEOUT": 300,
    }
}

CELERY_BROKER_URL = f"{REDIS_URL}/1"
CELERY_RESULT_BACKEND = f"{REDIS_URL}/2"
CELERY_BROKER_USE_SSL = REDIS_URL.startswith("rediss://")
CELERY_REDIS_BACKEND_USE_SSL = CELERY_BROKER_USE_SSL

# ---------------------------------------------------------------------------
# Inter-service: where to reach ProjectA
# ---------------------------------------------------------------------------
PROJECTA_HOST = env("PROJECTA_HOST", "")
PROJECTA_INTERNAL_URL = (
    f"https://{PROJECTA_HOST}" if PROJECTA_HOST else env("PROJECTA_INTERNAL_URL", "")
)

LOW_STOCK_THRESHOLD = int(env("LOW_STOCK_THRESHOLD", "10"))

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---------------------------------------------------------------------------
# Security headers
# ---------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------------------------
# CORS / CSRF
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    o.strip() for o in env("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()
]
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS + (
    [f"https://{RENDER_HOSTNAME}"] if RENDER_HOSTNAME else []
)

# ---------------------------------------------------------------------------
# DRF
# ---------------------------------------------------------------------------
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
    "rest_framework.renderers.JSONRenderer",
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", "INFO")},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "celery": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
