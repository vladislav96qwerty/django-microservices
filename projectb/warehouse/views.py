from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from .models import StockItem, StockMovement, Supplier, Warehouse
from .serializers import (
    BookSyncSerializer,
    StockItemSerializer,
    StockMovementSerializer,
    SupplierSerializer,
    WarehouseSerializer,
)
from .services import apply_book_sync


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name", "contact_email")


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name", "code", "location")
    lookup_field = "code"


class StockItemViewSet(viewsets.ModelViewSet):
    queryset = StockItem.objects.select_related("warehouse", "supplier")
    serializer_class = StockItemSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ("warehouse", "supplier")
    search_fields = ("isbn", "title")
    ordering_fields = ("quantity", "updated_at")

    @action(detail=False, methods=["get"])
    def low_stock(self, request):
        from django.conf import settings as dj_settings

        threshold = int(
            request.query_params.get("threshold", dj_settings.LOW_STOCK_THRESHOLD)
        )
        qs = self.get_queryset().filter(quantity__lte=threshold)
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(qs, many=True).data)


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.select_related("stock_item")
    serializer_class = StockMovementSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ("movement_type", "stock_item")
    ordering_fields = ("created_at",)

    def perform_create(self, serializer):
        movement = serializer.save(created_by=self.request.user.username or "api")
        # Apply quantity change directly to stock item
        item = movement.stock_item
        if movement.movement_type in {"in", "adjust", "transfer"}:
            item.quantity = max(0, item.quantity + movement.quantity)
        elif movement.movement_type == "out":
            item.quantity = max(0, item.quantity - abs(movement.quantity))
        item.save(update_fields=("quantity", "updated_at"))


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def sync_book(request):
    """Receive a book-state sync ping from ProjectA."""
    serializer = BookSyncSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    item = apply_book_sync(serializer.validated_data)
    return Response(StockItemSerializer(item).data, status=status.HTTP_200_OK)
