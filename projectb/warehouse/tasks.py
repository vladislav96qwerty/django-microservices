import logging

from celery import shared_task
from django.conf import settings

from .models import StockItem
from .services import apply_book_sync, fetch_books_from_projecta

logger = logging.getLogger(__name__)


@shared_task(name="warehouse.check_low_stock")
def check_low_stock() -> list[dict]:
    """Detect low-stock items and emit alerts (logs as the delivery mechanism)."""
    threshold = settings.LOW_STOCK_THRESHOLD
    alerts: list[dict] = []
    qs = StockItem.objects.filter(quantity__lte=threshold).select_related("warehouse")
    for item in qs:
        alert = {
            "warehouse": item.warehouse.code,
            "isbn": item.isbn,
            "title": item.title,
            "quantity": item.quantity,
            "reorder_level": item.reorder_level,
        }
        alerts.append(alert)
        logger.warning("LOW_STOCK_ALERT %s", alert)
    return alerts


@shared_task(name="warehouse.pull_books_from_projecta")
def pull_books_from_projecta() -> int:
    """Synchronize warehouse stock with the ProjectA catalog snapshot."""
    count = 0
    for row in fetch_books_from_projecta():
        try:
            apply_book_sync(row)
            count += 1
        except Exception:  # noqa: BLE001
            logger.exception("Failed to sync row %s", row)
    logger.info("Synced %s items from ProjectA", count)
    return count


@shared_task(name="warehouse.notify_supplier_for_reorder")
def notify_supplier_for_reorder(stock_item_id: int) -> bool:
    """Stub that would email a supplier when an item drops below reorder level."""
    try:
        item = StockItem.objects.select_related("supplier").get(pk=stock_item_id)
    except StockItem.DoesNotExist:
        return False
    if item.supplier and item.supplier.contact_email:
        logger.info(
            "Reorder request -> %s for %s (qty=%s)",
            item.supplier.contact_email,
            item.isbn,
            item.quantity,
        )
    return True
