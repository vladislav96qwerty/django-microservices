from django.db import transaction
from rest_framework import serializers

from books.models import Book

from .models import Order, OrderItem, OrderStatus


class OrderItemReadSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "book", "book_title", "quantity", "unit_price", "subtotal")


class OrderItemWriteSerializer(serializers.Serializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.filter(is_active=True))
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "status",
            "total",
            "shipping_address",
            "notes",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("status", "total", "user", "created_at", "updated_at")


class CreateOrderSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(max_length=255)
    notes = serializers.CharField(required=False, allow_blank=True)
    items = OrderItemWriteSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        items_data = validated_data.pop("items")
        order = Order.objects.create(
            user=user,
            shipping_address=validated_data["shipping_address"],
            notes=validated_data.get("notes", ""),
            status=OrderStatus.PENDING,
        )
        for item in items_data:
            book = item["book"]
            qty = item["quantity"]
            if book.stock < qty:
                raise serializers.ValidationError(
                    {"items": f"Not enough stock for '{book.title}'."}
                )
            book.stock -= qty
            book.save(update_fields=("stock",))
            OrderItem.objects.create(
                order=order, book=book, quantity=qty, unit_price=book.price
            )
        order.recalculate_total()
        return order
