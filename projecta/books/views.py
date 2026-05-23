from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from orders.permissions import IsReviewAuthorOrReadOnly

from .models import Author, Book, Category, Review
from .serializers import (
    AuthorSerializer,
    BookDetailSerializer,
    BookListSerializer,
    BookWriteSerializer,
    CategorySerializer,
    ReviewSerializer,
)


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name",)
    ordering_fields = ("name", "created_at")


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_field = "slug"


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related("author").prefetch_related("categories", "reviews")
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ("author", "categories", "language", "is_active")
    search_fields = ("title", "isbn", "author__name", "description")
    ordering_fields = ("price", "title", "created_at", "stock")
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        if self.action in {"create", "update", "partial_update"}:
            return BookWriteSerializer
        return BookDetailSerializer

    def list(self, request, *args, **kwargs):
        cache_key = f"books:list:{request.get_full_path()}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=120)
        return response

    @staticmethod
    def _invalidate_list_cache():
        # delete_pattern exists on django-redis; LocMemCache (tests) has only clear().
        if hasattr(cache, "delete_pattern"):
            cache.delete_pattern("projecta:books:list:*")
        else:
            cache.clear()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self._invalidate_list_cache()

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self._invalidate_list_cache()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        self._invalidate_list_cache()

    @action(detail=True, methods=["get"])
    def reviews(self, request, slug=None):
        book = self.get_object()
        qs = book.reviews.select_related("user").all()
        return Response(ReviewSerializer(qs, many=True).data)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("user", "book")
    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsReviewAuthorOrReadOnly,
    )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
