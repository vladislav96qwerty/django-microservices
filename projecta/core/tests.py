import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestHealth:
    def test_health_endpoint_responds(self, api_client):
        url = reverse("health")
        resp = api_client.get(url)
        # Redis may be unavailable in tests; the endpoint should still respond.
        assert resp.status_code in (200, 503)
        assert resp.data["service"] == "projecta"
        assert "checks" in resp.data
        assert "database" in resp.data["checks"]
        assert resp.data["checks"]["database"] is True
