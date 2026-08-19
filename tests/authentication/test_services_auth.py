import pytest
from rest_framework.exceptions import ValidationError

from ledger.authentication.services import create_token_pair, login_user, register_user


@pytest.mark.django_db
def test_register_user_returns_user_and_tokens(register_payload):
    """happy path: register_user creates a user and returns JWT tokens."""
    user, tokens = register_user(data=register_payload)

    assert user.username == register_payload["username"]
    assert user.check_password(register_payload["password"])
    assert "access" in tokens
    assert "refresh" in tokens


@pytest.mark.django_db
def test_register_user_rejects_duplicate_username(register_payload, user):
    """sad path: register_user rejects a username that is already taken."""
    duplicate_payload = {
        **register_payload,
        "username": user.username,
    }

    with pytest.raises(ValidationError):
        register_user(data=duplicate_payload)


@pytest.mark.django_db
def test_create_token_pair_returns_access_and_refresh(user):
    """happy path: create_token_pair returns both JWT token strings."""
    tokens = create_token_pair(user=user)

    assert tokens["access"]
    assert tokens["refresh"]


@pytest.mark.django_db
def test_login_user_returns_user_and_tokens(user, login_payload):
    """happy path: login_user authenticates valid credentials and returns tokens."""
    authenticated_user, tokens = login_user(
        username=login_payload["username"],
        password=login_payload["password"],
    )

    assert authenticated_user.id == user.id
    assert tokens["access"]
    assert tokens["refresh"]


@pytest.mark.django_db
def test_login_user_rejects_invalid_password(user, login_payload):
    """sad path: login_user rejects an incorrect password."""
    with pytest.raises(ValidationError):
        login_user(
            username=login_payload["username"],
            password="WrongPass1",
        )


@pytest.mark.django_db
def test_login_user_rejects_inactive_user(user, login_payload):
    """sad path: login_user rejects inactive accounts."""
    user.is_active = False
    user.save(update_fields=["is_active"])

    with pytest.raises(ValidationError):
        login_user(
            username=login_payload["username"],
            password=login_payload["password"],
        )
