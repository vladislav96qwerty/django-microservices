from django.contrib import admin

from .models import StockItem, StockMovement, Supplier, Warehouse


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "contact_email", "is_active", "created_at")
    search_fields = ("name", "contact_email")


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "location", "capacity", "is_active")
    search_fields = ("name", "code")


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ("id", "warehouse", "isbn", "title", "quantity", "reorder_level", "updated_at")
    list_filter = ("warehouse",)
    search_fields = ("isbn", "title")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("id", "stock_item", "movement_type", "quantity", "created_at")
    list_filter = ("movement_type",)
