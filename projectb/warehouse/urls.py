from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    StockItemViewSet,
    StockMovementViewSet,
    SupplierViewSet,
    WarehouseViewSet,
    sync_book,
)

router = DefaultRouter()
router.register(r"suppliers", SupplierViewSet, basename="supplier")
router.register(r"warehouses", WarehouseViewSet, basename="warehouse")
router.register(r"stock-items", StockItemViewSet, basename="stockitem")
router.register(r"movements", StockMovementViewSet, basename="movement")

urlpatterns = router.urls + [
    path("auth/login/", TokenObtainPairView.as_view(), name="warehouse-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="warehouse-refresh"),
    path("auth/verify/", TokenVerifyView.as_view(), name="warehouse-verify"),
    path("sync/book/", sync_book, name="sync-book"),
]
