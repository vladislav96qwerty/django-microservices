import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestUserModel:
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="bob", email="bob@example.com", password="P@ssw0rd!"
        )
        assert user.pk is not None
        assert user.check_password("P@ssw0rd!")
        assert user.preferred_language == "en"
        assert not user.is_verified

    def test_str(self):
        User = get_user_model()
        user = User(username="carl", email="carl@example.com")
        assert str(user) == "carl"


class TestRegister:
    def test_register_success(self, api_client):
        url = reverse("register")
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "VeryStrong!42",
            "password_confirm": "VeryStrong!42",
        }
        resp = api_client.post(url, payload)
        assert resp.status_code == 201
        assert resp.data["username"] == "newuser"

    def test_register_password_mismatch(self, api_client):
        url = reverse("register")
        payload = {
            "username": "x",
            "email": "x@example.com",
            "password": "VeryStrong!42",
            "password_confirm": "Different!",
        }
        resp = api_client.post(url, payload)
        assert resp.status_code == 400


class TestLogin:
    def test_login_returns_tokens(self, api_client, user):
        url = reverse("login")
        resp = api_client.post(url, {"username": "alice", "password": "StrongPass!234"})
        assert resp.status_code == 200
        assert "access" in resp.data
        assert "refresh" in resp.data

    def test_login_bad_credentials(self, api_client, user):
        url = reverse("login")
        resp = api_client.post(url, {"username": "alice", "password": "wrong"})
        assert resp.status_code == 401


class TestProfile:
    def test_get_profile(self, auth_client):
        url = reverse("profile")
        resp = auth_client.get(url)
        assert resp.status_code == 200
        assert resp.data["username"] == "alice"

    def test_anonymous_blocked(self, api_client):
        url = reverse("profile")
        resp = api_client.get(url)
        assert resp.status_code == 401

    def test_update_profile(self, auth_client):
        url = reverse("profile")
        resp = auth_client.patch(url, {"first_name": "Alice", "phone": "+380000"})
        assert resp.status_code == 200
        assert resp.data["first_name"] == "Alice"


class TestLogout:
    def test_logout_blacklists_refresh_token(self, api_client, user):
        login_url = reverse("login")
        login_resp = api_client.post(
            login_url, {"username": "alice", "password": "StrongPass!234"}
        )
        assert login_resp.status_code == 200
        access = login_resp.data["access"]
        refresh = login_resp.data["refresh"]

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        logout_url = reverse("logout")
        resp = api_client.post(logout_url, {"refresh": refresh}, format="json")
        assert resp.status_code == 205

        # Same refresh token should now be rejected
        refresh_url = reverse("token_refresh")
        retry = api_client.post(refresh_url, {"refresh": refresh}, format="json")
        assert retry.status_code == 401

    def test_logout_requires_refresh(self, auth_client):
        url = reverse("logout")
        resp = auth_client.post(url, {}, format="json")
        assert resp.status_code == 400

    def test_logout_rejects_bad_token(self, auth_client):
        url = reverse("logout")
        resp = auth_client.post(url, {"refresh": "not-a-token"}, format="json")
        assert resp.status_code == 400


class TestChangePassword:
    def test_change_password_ok(self, auth_client):
        url = reverse("change_password")
        resp = auth_client.post(
            url,
            {"old_password": "StrongPass!234", "new_password": "EvenStronger!99"},
        )
        assert resp.status_code == 200

    def test_change_password_wrong_old(self, auth_client):
        url = reverse("change_password")
        resp = auth_client.post(
            url,
            {"old_password": "nope", "new_password": "EvenStronger!99"},
        )
        assert resp.status_code == 400
