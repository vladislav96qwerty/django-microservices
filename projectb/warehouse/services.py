"""Cross-service synchronization helpers."""
import logging
from typing import Iterable

import requests
from django.conf import settings
from django.utils import timezone

from .models import StockItem, StockMovement, Warehouse

logger = logging.getLogger(__name__)


DEFAULT_WAREHOUSE_CODE = "MAIN"


def get_or_create_default_warehouse() -> Warehouse:
    wh, _ = Warehouse.objects.get_or_create(
        code=DEFAULT_WAREHOUSE_CODE,
        defaults={"name": "Main Warehouse", "location": "HQ"},
    )
    return wh


def apply_book_sync(payload: dict, warehouse: Warehouse | None = None) -> StockItem:
    """Update or create a StockItem from a ProjectA book payload."""
    warehouse = warehouse or get_or_create_default_warehouse()
    isbn = payload["isbn"]
    new_qty = int(payload["stock"])
    item, created = StockItem.objects.get_or_create(
        warehouse=warehouse,
        isbn=isbn,
        defaults={
            "book_id": payload["book_id"],
            "title": payload.get("title", ""),
            "quantity": new_qty,
        },
    )
    delta = new_qty - item.quantity
    item.book_id = payload["book_id"]
    item.title = payload.get("title", item.title)
    item.quantity = new_qty
    item.last_synced_at = timezone.now()
    item.save()

    if not created and delta != 0:
        StockMovement.objects.create(
            stock_item=item,
            movement_type="adjust",
            quantity=delta,
            reference="projecta-sync",
            note="Adjusted from ProjectA catalog sync",
            created_by="system",
        )
    return item


def fetch_books_from_projecta(token: str | None = None) -> Iterable[dict]:
    """Pull catalog data from ProjectA's public book listing."""
    url = f"{settings.PROJECTA_INTERNAL_URL}/api/books/"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    next_url = url
    while next_url:
        try:
            resp = requests.get(next_url, headers=headers, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.warning("ProjectA pull failed: %s", exc)
            return
        body = resp.json()
        for row in body.get("results", []):
            yield {
                "book_id": row["id"],
                "isbn": row["isbn"],
                "title": row["title"],
                "stock": row.get("stock", 0),
            }
        next_url = body.get("next")


def push_stock_update(book_id: int, new_quantity: int) -> bool:
    """Inform ProjectA of an authoritative stock change in the warehouse."""
    url = f"{settings.PROJECTA_INTERNAL_URL}/api/books/{book_id}/"
    try:
        resp = requests.patch(url, json={"stock": new_quantity}, timeout=5)
        return resp.ok
    except requests.RequestException as exc:
        logger.warning("Push to ProjectA failed: %s", exc)
        return False
