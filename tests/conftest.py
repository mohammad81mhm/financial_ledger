from uuid import uuid4

import pytest
from model_bakery import baker
from rest_framework.test import APIClient

from ledger.accounts.models import User
from ledger.accounts.services import create_user


@pytest.fixture
def api_client() -> APIClient:
    """Return an unauthenticated DRF API client."""
    return APIClient()


@pytest.fixture
def authenticated_api_client(user) -> APIClient:
    """Return a DRF API client authenticated as the default user."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def user_data() -> dict:
    """Return valid input data for creating a user."""
    return {
        "username": "wallet_user",
        "password": "SecurePass1",
        "first_name": "Wallet",
        "last_name": "User",
        "phone_number": "10000000001",
    }


@pytest.fixture
def other_user_data() -> dict:
    """Return valid input data for creating a second user."""
    return {
        "username": "other_user",
        "password": "SecurePass1",
        "first_name": "Other",
        "last_name": "User",
        "phone_number": "10000000002",
    }


@pytest.fixture
def user(db, user_data) -> User:
    """Return a persisted user with a known password."""
    return create_user(data=user_data)


@pytest.fixture
def other_user(db, other_user_data) -> User:
    """Return a second persisted user with a known password."""
    return create_user(data=other_user_data)


@pytest.fixture
def register_payload() -> dict:
    """Return unique registration payload for API tests."""
    suffix = uuid4().hex[:8]
    return {
        "username": f"register_user_{suffix}",
        "password": "SecurePass1",
        "first_name": "Register",
        "last_name": "User",
        "phone_number": f"100{suffix}0000"[:20],
    }


@pytest.fixture
def login_payload(user_data) -> dict:
    """Return login credentials for the default user."""
    return {
        "username": user_data["username"],
        "password": user_data["password"],
    }
