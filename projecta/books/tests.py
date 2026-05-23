from decimal import Decimal

import pytest
from django.urls import reverse

from books.models import Author, Book, Category, Review

pytestmark = pytest.mark.django_db


@pytest.fixture
def author(db):
    return Author.objects.create(name="George Orwell")


@pytest.fixture
def category(db):
    return Category.objects.create(name="Fiction", slug="fiction")


@pytest.fixture
def book(db, author, category):
    b = Book.objects.create(
        title="1984",
        slug="1984",
        isbn="9780451524935",
        author=author,
        description="Dystopian classic",
        price=Decimal("12.50"),
        stock=10,
        pages=328,
    )
    b.categories.add(category)
    return b


class TestBookModel:
    def test_is_in_stock(self, book):
        assert book.is_in_stock is True
        book.stock = 0
        book.save()
        assert book.is_in_stock is False

    def test_str(self, book):
        assert "1984" in str(book)


class TestBookList:
    def test_list_anonymous(self, api_client, book):
        url = reverse("book-list")
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert resp.data["count"] == 1
        assert resp.data["results"][0]["title"] == "1984"

    def test_search(self, api_client, book):
        url = reverse("book-list")
        resp = api_client.get(url, {"search": "Orwell"})
        assert resp.status_code == 200
        assert resp.data["count"] == 1

    def test_filter_by_language(self, api_client, book):
        url = reverse("book-list")
        resp = api_client.get(url, {"language": "en"})
        assert resp.status_code == 200


class TestBookDetail:
    def test_retrieve(self, api_client, book):
        url = reverse("book-detail", args=[book.slug])
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert resp.data["title"] == "1984"
        assert resp.data["author"]["name"] == "George Orwell"


class TestBookWrite:
    def test_create_requires_auth(self, api_client, author):
        url = reverse("book-list")
        resp = api_client.post(url, {})
        assert resp.status_code in (401, 403)

    def test_create_authenticated(self, auth_client, author):
        url = reverse("book-list")
        resp = auth_client.post(
            url,
            {
                "title": "Animal Farm",
                "slug": "animal-farm",
                "isbn": "9780451526342",
                "author": author.pk,
                "price": "9.99",
                "stock": 5,
                "pages": 112,
                "language": "en",
                "is_active": True,
            },
            format="json",
        )
        assert resp.status_code == 201


class TestReview:
    def test_create_review(self, auth_client, book):
        url = reverse("review-list")
        resp = auth_client.post(
            url, {"book": book.pk, "rating": 5, "text": "Excellent!"}, format="json"
        )
        assert resp.status_code == 201

    def test_rating_bounds(self, auth_client, book):
        url = reverse("review-list")
        resp = auth_client.post(url, {"book": book.pk, "rating": 9, "text": "Bad"}, format="json")
        assert resp.status_code == 400


class TestAuthor:
    def test_list(self, api_client, author):
        url = reverse("author-list")
        resp = api_client.get(url)
        assert resp.status_code == 200


class TestCategory:
    def test_list(self, api_client, category):
        url = reverse("category-list")
        resp = api_client.get(url)
        assert resp.status_code == 200
