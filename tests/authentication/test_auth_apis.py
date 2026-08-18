import pytest
from rest_framework import status

from ledger.accounts.models import User


@pytest.mark.django_db
class TestRegisterApi:
    """Tests for POST /api/authentication/register/."""

    def test_creates_user_and_returns_tokens(self, api_client, register_url, register_payload):
        """happy path: register API creates a user and returns JWT tokens."""
        response = api_client.post(register_url, register_payload, format="json")
        result = response.json()["result"]

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username=register_payload["username"]).exists()
        assert result["user"]["username"] == register_payload["username"]
        assert result["tokens"]["access"]
        assert result["tokens"]["refresh"]

    def test_rejects_duplicate_username(self, api_client, register_url, register_payload, user):
        """sad path: register API rejects a username that is already taken."""
        duplicate_payload = {
            **register_payload,
            "phone_number": "10000000999",
            "username": user.username,
        }

        response = api_client.post(register_url, duplicate_payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rejects_short_password(self, api_client, register_url, register_payload):
        """sad path: register API rejects passwords shorter than eight characters."""
        invalid_payload = {
            **register_payload,
            "password": "short",
        }

        response = api_client.post(register_url, invalid_payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginApi:
    """Tests for POST /api/authentication/login/."""

    def test_returns_user_and_tokens(self, api_client, user, login_url, login_payload):
        """happy path: login API returns the authenticated user and JWT tokens."""
        response = api_client.post(login_url, login_payload, format="json")
        result = response.json()["result"]

        assert response.status_code == status.HTTP_200_OK
        assert result["user"]["username"] == user.username
        assert result["tokens"]["access"]
        assert result["tokens"]["refresh"]

    def test_rejects_invalid_credentials(self, api_client, login_url, login_payload):
        """sad path: login API rejects invalid username or password."""
        response = api_client.post(
            login_url,
            {
                "username": login_payload["username"],
                "password": "WrongPass1",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_token_grants_access_to_protected_endpoint(
        self,
        api_client,
        user,
        login_url,
        login_payload,
        transaction_list_url,
    ):
        """happy path: access token from login authorizes protected transaction endpoints."""
        login_response = api_client.post(login_url, login_payload, format="json")
        access_token = login_response.json()["result"]["tokens"]["access"]

        response = api_client.get(
            transaction_list_url,
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )

        assert response.status_code == status.HTTP_200_OK
