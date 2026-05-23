import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Supplier",
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
                    models.CharField(max_length=255, unique=True, verbose_name="name"),
                ),
                (
                    "contact_email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="contact email"
                    ),
                ),
                (
                    "phone",
                    models.CharField(blank=True, max_length=32, verbose_name="phone"),
                ),
                (
                    "address",
                    models.CharField(blank=True, max_length=255, verbose_name="address"),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="Warehouse",
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
                    models.CharField(max_length=255, unique=True, verbose_name="name"),
                ),
                (
                    "code",
                    models.CharField(max_length=32, unique=True, verbose_name="code"),
                ),
                (
                    "location",
                    models.CharField(blank=True, max_length=255, verbose_name="location"),
                ),
                (
                    "capacity",
                    models.PositiveIntegerField(default=0, verbose_name="capacity"),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ("code",)},
        ),
        migrations.CreateModel(
            name="StockItem",
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
                    "book_id",
                    models.PositiveIntegerField(
                        db_index=True, verbose_name="ProjectA book id"
                    ),
                ),
                (
                    "isbn",
                    models.CharField(db_index=True, max_length=20, verbose_name="ISBN"),
                ),
                (
                    "title",
                    models.CharField(blank=True, max_length=255, verbose_name="title"),
                ),
                (
                    "quantity",
                    models.PositiveIntegerField(default=0, verbose_name="quantity"),
                ),
                (
                    "reorder_level",
                    models.PositiveIntegerField(
                        default=10, verbose_name="reorder level"
                    ),
                ),
                ("last_synced_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "supplier",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="stock_items",
                        to="warehouse.supplier",
                    ),
                ),
                (
                    "warehouse",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stock_items",
                        to="warehouse.warehouse",
                    ),
                ),
            ],
            options={
                "ordering": ("warehouse", "isbn"),
                "unique_together": {("warehouse", "isbn")},
            },
        ),
        migrations.AddIndex(
            model_name="stockitem",
            index=models.Index(fields=["isbn"], name="warehouse_s_isbn_idx"),
        ),
        migrations.AddIndex(
            model_name="stockitem",
            index=models.Index(fields=["book_id"], name="warehouse_s_book_id_idx"),
        ),
        migrations.CreateModel(
            name="StockMovement",
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
                    "movement_type",
                    models.CharField(
                        choices=[
                            ("in", "Inbound"),
                            ("out", "Outbound"),
                            ("adjust", "Adjustment"),
                            ("transfer", "Transfer"),
                        ],
                        max_length=10,
                        verbose_name="movement type",
                    ),
                ),
                ("quantity", models.IntegerField(verbose_name="quantity")),
                (
                    "reference",
                    models.CharField(blank=True, max_length=128, verbose_name="reference"),
                ),
                ("note", models.TextField(blank=True, verbose_name="note")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.CharField(blank=True, max_length=128, verbose_name="created by"),
                ),
                (
                    "stock_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="movements",
                        to="warehouse.stockitem",
                    ),
                ),
            ],
            options={"ordering": ("-created_at",)},
        ),
    ]
