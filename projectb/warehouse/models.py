from django.db import models
from django.utils.translation import gettext_lazy as _


class Supplier(models.Model):
    name = models.CharField(_("name"), max_length=255, unique=True)
    contact_email = models.EmailField(_("contact email"), blank=True)
    phone = models.CharField(_("phone"), max_length=32, blank=True)
    address = models.CharField(_("address"), max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Warehouse(models.Model):
    name = models.CharField(_("name"), max_length=255, unique=True)
    code = models.CharField(_("code"), max_length=32, unique=True)
    location = models.CharField(_("location"), max_length=255, blank=True)
    capacity = models.PositiveIntegerField(_("capacity"), default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("code",)

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class StockItem(models.Model):
    """A specific book SKU stored in a specific warehouse."""

    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="stock_items"
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="stock_items"
    )
    book_id = models.PositiveIntegerField(_("ProjectA book id"), db_index=True)
    isbn = models.CharField(_("ISBN"), max_length=20, db_index=True)
    title = models.CharField(_("title"), max_length=255, blank=True)
    quantity = models.PositiveIntegerField(_("quantity"), default=0)
    reorder_level = models.PositiveIntegerField(_("reorder level"), default=10)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("warehouse", "isbn")
        ordering = ("warehouse", "isbn")
        indexes = [
            models.Index(fields=["isbn"]),
            models.Index(fields=["book_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.isbn} @ {self.warehouse.code} ({self.quantity})"

    @property
    def is_low_stock(self) -> bool:
        return self.quantity <= self.reorder_level


class MovementType(models.TextChoices):
    IN = "in", _("Inbound")
    OUT = "out", _("Outbound")
    ADJUST = "adjust", _("Adjustment")
    TRANSFER = "transfer", _("Transfer")


class StockMovement(models.Model):
    stock_item = models.ForeignKey(
        StockItem, on_delete=models.CASCADE, related_name="movements"
    )
    movement_type = models.CharField(
        _("movement type"), max_length=10, choices=MovementType.choices
    )
    quantity = models.IntegerField(_("quantity"))
    reference = models.CharField(_("reference"), max_length=128, blank=True)
    note = models.TextField(_("note"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(_("created by"), max_length=128, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.movement_type} {self.quantity} on {self.stock_item_id}"
