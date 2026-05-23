from decimal import Decimal

import pytest
from django.urls import reverse

from books.models import Author, Book
from orders.models import Order, OrderStatus

pytestmark = pytest.mark.django_db


@pytest.fixture
def book(db):
    author = Author.objects.create(name="Frank Herbert")
    return Book.objects.create(
        title="Dune",
        slug="dune",
        isbn="9780441172719",
        author=author,
        price=Decimal("15.00"),
        stock=5,
        pages=688,
    )


class TestOrderCreate:
    def test_unauthenticated_blocked(self, api_client, book):
        url = reverse("order-list")
        resp = api_client.post(url, {})
        assert resp.status_code == 401

    def test_create_order(self, auth_client, book):
        url = reverse("order-list")
        payload = {
            "shipping_address": "1 Main St",
            "items": [{"book": book.pk, "quantity": 2}],
        }
        resp = auth_client.post(url, payload, format="json")
        assert resp.status_code == 201
        assert resp.data["total"] == "30.00"
        book.refresh_from_db()
        assert book.stock == 3

    def test_create_over_stock(self, auth_client, book):
        url = reverse("order-list")
        payload = {
            "shipping_address": "1 Main St",
            "items": [{"book": book.pk, "quantity": 99}],
        }
        resp = auth_client.post(url, payload, format="json")
        assert resp.status_code == 400


class TestOrderList:
    def test_user_sees_only_own(self, auth_client, user, book):
        Order.objects.create(user=user, shipping_address="x", total=Decimal("0.00"))
        url = reverse("order-list")
        resp = auth_client.get(url)
        assert resp.status_code == 200
        assert resp.data["count"] == 1


class TestOrderCancel:
    def test_cancel_restores_stock(self, auth_client, user, book):
        from orders.models import OrderItem

        order = Order.objects.create(user=user, shipping_address="x")
        OrderItem.objects.create(order=order, book=book, quantity=2, unit_price=book.price)
        book.stock -= 2
        book.save()
        url = reverse("order-cancel", args=[order.pk])
        resp = auth_client.post(url)
        assert resp.status_code == 200
        book.refresh_from_db()
        assert book.stock == 5
        order.refresh_from_db()
        assert order.status == OrderStatus.CANCELLED
