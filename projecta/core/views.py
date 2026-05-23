import logging

import redis
from django.conf import settings
from django.db import connection
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def _check_database() -> bool:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return True
    except Exception:  # noqa: BLE001
        logger.exception("DB health check failed")
        return False


def _check_redis() -> bool:
    try:
        r = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        return bool(r.ping())
    except Exception:  # noqa: BLE001
        logger.exception("Redis health check failed")
        return False


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    checks = {"database": _check_database(), "redis": _check_redis()}
    ok = all(checks.values())
    payload = {
        "service": "projecta",
        "status": "ok" if ok else "degraded",
        "checks": checks,
    }
    code = status.HTTP_200_OK if ok else status.HTTP_503_SERVICE_UNAVAILABLE
    return Response(payload, status=code)
