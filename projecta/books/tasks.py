import logging

import requests
from celery import shared_task
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


@shared_task(name="books.invalidate_book_caches")
def invalidate_book_caches() -> int:
    """Periodic cache cleanup."""
    try:
        return cache.delete_pattern("projecta:books:list:*")
    except Exception:  # noqa: BLE001
        logger.exception("Cache invalidation failed")
        return 0


@shared_task(name="books.notify_warehouse_of_book", bind=True, max_retries=3, default_retry_delay=10)
def notify_warehouse_of_book(self, book_id: int, isbn: str, title: str, stock: int):
    """Notify ProjectB warehouse service when a book's catalog entry changes."""
    url = f"{settings.PROJECTB_INTERNAL_URL}/warehouse/api/sync/book/"
    try:
        response = requests.post(
            url,
            json={"book_id": book_id, "isbn": isbn, "title": title, "stock": stock},
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        logger.warning("Warehouse sync failed for book %s: %s", book_id, exc)
        raise self.retry(exc=exc)
