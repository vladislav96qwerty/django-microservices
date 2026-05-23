from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Author",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_index=True, max_length=255, verbose_name="name"
                    ),
                ),
                ("bio", models.TextField(blank=True, verbose_name="biography")),
                (
                    "birth_date",
                    models.DateField(blank=True, null=True, verbose_name="birth date"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "author",
                "verbose_name_plural": "authors",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=128, unique=True, verbose_name="name"),
                ),
                ("slug", models.SlugField(unique=True)),
            ],
            options={
                "verbose_name": "category",
                "verbose_name_plural": "categories",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        db_index=True, max_length=255, verbose_name="title"
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        max_length=255, unique=True, verbose_name="slug"
                    ),
                ),
                (
                    "isbn",
                    models.CharField(
                        max_length=20, unique=True, verbose_name="ISBN"
                    ),
                ),
                ("description", models.TextField(blank=True, verbose_name="description")),
                (
                    "cover",
                    models.ImageField(
                        blank=True, null=True, upload_to="covers/", verbose_name="cover"
                    ),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0.00"))
                        ],
                        verbose_name="price",
                    ),
                ),
                (
                    "stock",
                    models.PositiveIntegerField(default=0, verbose_name="stock"),
                ),
                (
                    "pages",
                    models.PositiveIntegerField(default=0, verbose_name="pages"),
                ),
                (
                    "language",
                    models.CharField(default="en", max_length=10, verbose_name="language"),
                ),
                (
                    "publication_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="publication date"
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="active"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="books",
                        to="books.author",
                        verbose_name="author",
                    ),
                ),
                (
                    "categories",
                    models.ManyToManyField(
                        blank=True, related_name="books", to="books.category"
                    ),
                ),
            ],
            options={
                "verbose_name": "book",
                "verbose_name_plural": "books",
                "ordering": ("-created_at",),
            },
        ),
        migrations.AddIndex(
            model_name="book",
            index=models.Index(fields=["title"], name="books_book_title_idx"),
        ),
        migrations.AddIndex(
            model_name="book",
            index=models.Index(fields=["isbn"], name="books_book_isbn_idx"),
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "rating",
                    models.PositiveSmallIntegerField(verbose_name="rating"),
                ),
                ("text", models.TextField(blank=True, verbose_name="text")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "book",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="books.book",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
                "unique_together": {("book", "user")},
            },
        ),
    ]
