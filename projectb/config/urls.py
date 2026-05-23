from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("", RedirectView.as_view(url="/warehouse/api/docs/", permanent=False)),
    path("warehouse-admin/", admin.site.urls),
    path("warehouse/api/", include("warehouse.urls")),
    path("warehouse/api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("warehouse/api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("", include("core.urls")),
]
