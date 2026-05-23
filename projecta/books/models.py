from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    name = models.CharField(_("name"), max_length=255, db_index=True)
    bio = models.TextField(_("biography"), blank=True)
    birth_date = models.DateField(_("birth date"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)
        verbose_name = _("author")
        verbose_name_plural = _("authors")

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    name = models.CharField(_("name"), max_length=128, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    title = models.CharField(_("title"), max_length=255, db_index=True)
    slug = models.SlugField(_("slug"), max_length=255, unique=True)
    isbn = models.CharField(_("ISBN"), max_length=20, unique=True)
    author = models.ForeignKey(
        Author, on_delete=models.PROTECT, related_name="books", verbose_name=_("author")
    )
    categories = models.ManyToManyField(Category, related_name="books", blank=True)
    description = models.TextField(_("description"), blank=True)
    cover = models.ImageField(_("cover"), upload_to="covers/", blank=True, null=True)
    price = models.DecimalField(
        _("price"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    stock = models.PositiveIntegerField(_("stock"), default=0)
    pages = models.PositiveIntegerField(_("pages"), default=0)
    language = models.CharField(_("language"), max_length=10, default="en")
    publication_date = models.DateField(_("publication date"), null=True, blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("book")
        verbose_name_plural = _("books")
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["isbn"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.isbn})"

    @property
    def is_in_stock(self) -> bool:
        return self.stock > 0


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(_("rating"))
    text = models.TextField(_("text"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        unique_together = ("book", "user")

    def __str__(self) -> str:
        return f"Review {self.rating}/5 by {self.user_id} on {self.book_id}"
