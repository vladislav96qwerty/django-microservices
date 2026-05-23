import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestHealth:
    def test_health(self, api_client):
        url = reverse("health")
        resp = api_client.get(url)
        assert resp.status_code in (200, 503)
        assert resp.data["service"] == "projectb"
        assert resp.data["checks"]["database"] is True
