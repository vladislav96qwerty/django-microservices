import pytest
from django.urls import reverse

from warehouse.models import (
    MovementType,
    StockItem,
    StockMovement,
    Supplier,
    Warehouse,
)
from warehouse.services import apply_book_sync, get_or_create_default_warehouse
from warehouse.tasks import check_low_stock

pytestmark = pytest.mark.django_db


@pytest.fixture
def warehouse(db):
    return Warehouse.objects.create(name="Main", code="MAIN", capacity=10000)


@pytest.fixture
def supplier(db):
    return Supplier.objects.create(name="Big Books Inc", contact_email="sales@bigbooks.example")


@pytest.fixture
def stock_item(db, warehouse):
    return StockItem.objects.create(
        warehouse=warehouse,
        book_id=1,
        isbn="9780451524935",
        title="1984",
        quantity=20,
        reorder_level=10,
    )


class TestWarehouseModel:
    def test_str(self, warehouse):
        assert "MAIN" in str(warehouse)


class TestStockItemModel:
    def test_low_stock_flag(self, stock_item):
        assert stock_item.is_low_stock is False
        stock_item.quantity = 5
        stock_item.save()
        assert stock_item.is_low_stock is True


class TestSupplierEndpoint:
    def test_requires_auth(self, api_client):
        url = reverse("supplier-list")
        resp = api_client.get(url)
        assert resp.status_code == 401

    def test_list(self, auth_client, supplier):
        url = reverse("supplier-list")
        resp = auth_client.get(url)
        assert resp.status_code == 200
        assert resp.data["count"] == 1

    def test_create(self, auth_client):
        url = reverse("supplier-list")
        resp = auth_client.post(url, {"name": "Acme", "contact_email": "x@x.com"}, format="json")
        assert resp.status_code == 201


class TestWarehouseEndpoint:
    def test_create(self, auth_client):
        url = reverse("warehouse-list")
        resp = auth_client.post(
            url, {"name": "North", "code": "N1", "capacity": 100}, format="json"
        )
        assert resp.status_code == 201


class TestStockItemEndpoint:
    def test_list(self, auth_client, stock_item):
        url = reverse("stockitem-list")
        resp = auth_client.get(url)
        assert resp.status_code == 200
        assert resp.data["count"] == 1

    def test_low_stock_endpoint(self, auth_client, stock_item):
        stock_item.quantity = 3
        stock_item.save()
        url = reverse("stockitem-low-stock")
        resp = auth_client.get(url)
        assert resp.status_code == 200
        results = resp.data.get("results", resp.data)
        assert len(results) == 1


class TestStockMovementEndpoint:
    def test_inbound_increments_quantity(self, auth_client, stock_item):
        url = reverse("movement-list")
        resp = auth_client.post(
            url,
            {
                "stock_item": stock_item.pk,
                "movement_type": MovementType.IN,
                "quantity": 5,
            },
            format="json",
        )
        assert resp.status_code == 201
        stock_item.refresh_from_db()
        assert stock_item.quantity == 25

    def test_outbound_decrements(self, auth_client, stock_item):
        url = reverse("movement-list")
        resp = auth_client.post(
            url,
            {
                "stock_item": stock_item.pk,
                "movement_type": MovementType.OUT,
                "quantity": 7,
            },
            format="json",
        )
        assert resp.status_code == 201
        stock_item.refresh_from_db()
        assert stock_item.quantity == 13


class TestBookSyncEndpoint:
    def test_sync_creates_stock_item(self, api_client):
        url = reverse("sync-book")
        payload = {
            "book_id": 42,
            "isbn": "9780000000000",
            "title": "New Book",
            "stock": 11,
        }
        resp = api_client.post(url, payload, format="json")
        assert resp.status_code == 200
        assert StockItem.objects.filter(isbn="9780000000000").exists()

    def test_sync_updates_existing(self, api_client, stock_item):
        url = reverse("sync-book")
        payload = {
            "book_id": stock_item.book_id,
            "isbn": stock_item.isbn,
            "title": stock_item.title,
            "stock": 99,
        }
        resp = api_client.post(url, payload, format="json")
        assert resp.status_code == 200
        stock_item.refresh_from_db()
        assert stock_item.quantity == 99
        assert StockMovement.objects.filter(stock_item=stock_item).count() == 1


class TestServices:
    def test_default_warehouse(self, db):
        wh = get_or_create_default_warehouse()
        assert wh.code == "MAIN"
        # idempotent
        again = get_or_create_default_warehouse()
        assert again.pk == wh.pk

    def test_apply_book_sync(self, db):
        item = apply_book_sync({"book_id": 1, "isbn": "X", "title": "T", "stock": 4})
        assert item.quantity == 4


class TestLowStockTask:
    def test_check_low_stock(self, db, warehouse):
        StockItem.objects.create(
            warehouse=warehouse, book_id=1, isbn="A", title="A", quantity=2, reorder_level=10
        )
        StockItem.objects.create(
            warehouse=warehouse, book_id=2, isbn="B", title="B", quantity=99, reorder_level=10
        )
        alerts = check_low_stock()
        assert len(alerts) == 1
        assert alerts[0]["isbn"] == "A"
