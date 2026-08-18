import pytest
from rest_framework import status

from ledger.accounts.models import User


@pytest.mark.django_db
def test_register_api_creates_user_and_returns_tokens(api_client, register_payload):
    """happy path: register API creates a user and returns JWT tokens."""
    response = api_client.post(
        "/api/authentication/register/",
        register_payload,
        format="json",
    )
    result = response.json()["result"]

    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(username=register_payload["username"]).exists()
    assert result["user"]["username"] == register_payload["username"]
    assert result["tokens"]["access"]
    assert result["tokens"]["refresh"]


@pytest.mark.django_db
def test_register_api_rejects_duplicate_username(api_client, register_payload, user):
    """sad path: register API rejects a username that is already taken."""
    duplicate_payload = {
        **register_payload,
        "phone_number": "10000000999",
        "username": user.username,
    }

    response = api_client.post(
        "/api/authentication/register/",
        duplicate_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_api_rejects_short_password(api_client, register_payload):
    """sad path: register API rejects passwords shorter than eight characters."""
    invalid_payload = {
        **register_payload,
        "password": "short",
    }

    response = api_client.post(
        "/api/authentication/register/",
        invalid_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_api_returns_user_and_tokens(api_client, user, login_payload):
    """happy path: login API returns the authenticated user and JWT tokens."""
    response = api_client.post(
        "/api/authentication/login/",
        login_payload,
        format="json",
    )
    result = response.json()["result"]

    assert response.status_code == status.HTTP_200_OK
    assert result["user"]["username"] == user.username
    assert result["tokens"]["access"]
    assert result["tokens"]["refresh"]


@pytest.mark.django_db
def test_login_api_rejects_invalid_credentials(api_client, login_payload):
    """sad path: login API rejects invalid username or password."""
    response = api_client.post(
        "/api/authentication/login/",
        {
            "username": login_payload["username"],
            "password": "WrongPass1",
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_token_grants_access_to_protected_endpoint(api_client, user, login_payload):
    """happy path: access token from login authorizes protected transaction endpoints."""
    login_response = api_client.post(
        "/api/authentication/login/",
        login_payload,
        format="json",
    )
    access_token = login_response.json()["result"]["tokens"]["access"]

    response = api_client.get(
        "/api/transactions/",
        HTTP_AUTHORIZATION=f"Bearer {access_token}",
    )

    assert response.status_code == status.HTTP_200_OK
