from rest_framework import serializers

from .models import StockItem, StockMovement, Supplier, Warehouse


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ("id", "name", "contact_email", "phone", "address", "is_active", "created_at")


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ("id", "name", "code", "location", "capacity", "is_active", "created_at")


class StockItemSerializer(serializers.ModelSerializer):
    warehouse_code = serializers.CharField(source="warehouse.code", read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = StockItem
        fields = (
            "id",
            "warehouse",
            "warehouse_code",
            "supplier",
            "book_id",
            "isbn",
            "title",
            "quantity",
            "reorder_level",
            "is_low_stock",
            "last_synced_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("last_synced_at", "created_at", "updated_at")


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = (
            "id",
            "stock_item",
            "movement_type",
            "quantity",
            "reference",
            "note",
            "created_at",
            "created_by",
        )
        read_only_fields = ("created_at",)


class BookSyncSerializer(serializers.Serializer):
    """Payload accepted from ProjectA when its catalog changes."""

    book_id = serializers.IntegerField()
    isbn = serializers.CharField(max_length=20)
    title = serializers.CharField(max_length=255, required=False, allow_blank=True)
    stock = serializers.IntegerField(min_value=0)
    warehouse_code = serializers.CharField(max_length=32, required=False, allow_blank=True)
