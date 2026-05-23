from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Order, OrderStatus
from .permissions import IsOrderOwner
from .serializers import CreateOrderSerializer, OrderSerializer


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (permissions.IsAuthenticated, IsOrderOwner)
    # drf-spectacular calls get_queryset() during schema generation with an
    # AnonymousUser, which breaks our user filter. The empty fallback lets
    # the schema introspect the model without exploding.
    queryset = Order.objects.none()

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items__book")
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return CreateOrderSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status in {OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED}:
            return Response(
                {"detail": f"Cannot cancel order in '{order.status}' status."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # restore stock
        for item in order.items.select_related("book"):
            item.book.stock += item.quantity
            item.book.save(update_fields=("stock",))
        order.status = OrderStatus.CANCELLED
        order.save(update_fields=("status", "updated_at"))
        return Response(OrderSerializer(order).data)
