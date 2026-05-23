from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from books.models import Author, Book
from orders.models import Order

pytestmark = pytest.mark.django_db


def _auth_client(user):
    client = APIClient()
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return client


@pytest.fixture
def book(db):
    author = Author.objects.create(name="Author X")
    return Book.objects.create(
        title="Book X",
        slug="book-x",
        isbn="9990000000001",
        author=author,
        price=Decimal("10.00"),
        stock=5,
        pages=100,
    )


class TestIsOrderOwner:
    def test_user_cannot_read_someone_elses_order(self, book):
        User = get_user_model()
        alice = User.objects.create_user(
            username="alice_o", email="alice_o@x.com", password="pw!12345"
        )
        bob = User.objects.create_user(
            username="bob_o", email="bob_o@x.com", password="pw!12345"
        )
        order = Order.objects.create(user=alice, shipping_address="A")
        url = reverse("order-detail", args=[order.pk])

        # Bob tries to read Alice's order — list filters by user so 404 here,
        # but the object-level guard makes the result deterministic.
        bob_client = _auth_client(bob)
        resp = bob_client.get(url)
        assert resp.status_code in (403, 404)

    def test_owner_can_read_own_order(self, book):
        User = get_user_model()
        alice = User.objects.create_user(
            username="alice2", email="alice2@x.com", password="pw!12345"
        )
        order = Order.objects.create(user=alice, shipping_address="A")
        url = reverse("order-detail", args=[order.pk])
        resp = _auth_client(alice).get(url)
        assert resp.status_code == 200

    def test_staff_can_read_any_order(self, book):
        User = get_user_model()
        alice = User.objects.create_user(
            username="alice3", email="alice3@x.com", password="pw!12345"
        )
        admin = User.objects.create_user(
            username="admin_o", email="admin_o@x.com", password="pw!12345", is_staff=True
        )
        order = Order.objects.create(user=alice, shipping_address="A")
        url = reverse("order-detail", args=[order.pk])
        # The default get_queryset filters by user, so admin's queryset is empty
        # by design. The permission class itself, however, would allow it — this
        # test documents the permission's behavior at the class level.
        from orders.permissions import IsOrderOwner

        class _Req:
            user = admin

        assert IsOrderOwner().has_object_permission(_Req(), None, order) is True


class TestIsReviewAuthorOrReadOnly:
    def test_anyone_can_read_reviews(self, book):
        client = APIClient()
        url = reverse("review-list")
        resp = client.get(url)
        assert resp.status_code == 200

    def test_only_author_can_edit_review(self, book):
        User = get_user_model()
        author = User.objects.create_user(
            username="rev_author", email="ra@x.com", password="pw!12345"
        )
        other = User.objects.create_user(
            username="rev_other", email="ro@x.com", password="pw!12345"
        )
        # author creates a review
        author_client = _auth_client(author)
        url = reverse("review-list")
        create_resp = author_client.post(
            url, {"book": book.pk, "rating": 5, "text": "Great"}, format="json"
        )
        assert create_resp.status_code == 201
        review_id = create_resp.data["id"]
        # other user tries to edit
        other_client = _auth_client(other)
        patch_url = reverse("review-detail", args=[review_id])
        resp = other_client.patch(patch_url, {"rating": 1}, format="json")
        assert resp.status_code == 403
